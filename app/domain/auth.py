import hashlib
import hmac
import os
import re
import secrets
from datetime import date

import pandas as pd

from models import AppSetting, SessionLocal, User


PBKDF2_ALGO = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260000
RELEASE_DEFAULT_ADMIN_USER = "admin"
RELEASE_DEFAULT_ADMIN_PASSWORD = "admin123"
RELEASE_DEFAULT_ADMIN_FULL_NAME = "Administrator"
DEFAULT_ADMIN_SEEDED_KEY = "auth.default_admin_seeded"
USER_ALLOWED_ROLES = {"admin", "user"}


def _norm_text(val):
    if val is None:
        return ""
    return str(val).replace("\u00A0", " ").strip()


def _hash_password_legacy_sha256(password):
    return hashlib.sha256(password.encode()).hexdigest()


def _hash_password_pbkdf2(password, *, iterations=PBKDF2_ITERATIONS):
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"{PBKDF2_ALGO}${iterations}${salt}${dk.hex()}"


def hash_password(password):
    return _hash_password_pbkdf2(password)


def verify_password(password, password_hash):
    stored = str(password_hash or "").strip()
    if not stored:
        return False

    parts = stored.split("$")
    if len(parts) == 4 and parts[0] == PBKDF2_ALGO:
        try:
            iterations = int(parts[1])
            salt = parts[2]
            expected_hex = parts[3]
            calc = hashlib.pbkdf2_hmac(
                "sha256",
                str(password or "").encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            ).hex()
            return hmac.compare_digest(calc, expected_hex)
        except Exception:
            return False

    if re.fullmatch(r"[0-9a-fA-F]{64}", stored):
        return hmac.compare_digest(_hash_password_legacy_sha256(str(password or "")), stored.lower())

    return False


def _is_strong_bootstrap_password(password):
    if not password or len(password) < 10:
        return False
    has_lower = any(ch.islower() for ch in password)
    has_upper = any(ch.isupper() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    return has_lower and has_upper and has_digit


def _bootstrap_admin_if_enabled(session):
    enabled = os.environ.get("APP_BOOTSTRAP_ADMIN", "0").strip().lower() in ("1", "true", "yes")
    if not enabled:
        return

    username = (os.environ.get("APP_BOOTSTRAP_ADMIN_USER", "admin") or "admin").strip()
    full_name = (os.environ.get("APP_BOOTSTRAP_ADMIN_FULL_NAME", "Administrator") or "Administrator").strip()
    raw_password = (os.environ.get("APP_BOOTSTRAP_ADMIN_PASSWORD", "") or "").strip()

    if session.query(User).filter_by(username=username).first():
        return
    if not _is_strong_bootstrap_password(raw_password):
        print("Security bootstrap skipped: APP_BOOTSTRAP_ADMIN_PASSWORD must be >=10 chars and include upper/lower/digit.")
        return

    session.add(
        User(
            username=username,
            password_hash=hash_password(raw_password),
            full_name=full_name,
            role="admin",
            created_date=str(date.today()),
        )
    )
    session.commit()


def _mark_default_admin_seeded(session):
    setting = session.query(AppSetting).filter_by(key=DEFAULT_ADMIN_SEEDED_KEY).first()
    if setting:
        setting.value = "1"
        return
    session.add(AppSetting(key=DEFAULT_ADMIN_SEEDED_KEY, value="1"))


def _ensure_release_default_admin(session):
    seeded = session.query(AppSetting).filter_by(key=DEFAULT_ADMIN_SEEDED_KEY).first()
    if seeded:
        return

    existing_user = session.query(User.username).first()
    if existing_user:
        _mark_default_admin_seeded(session)
        session.commit()
        return

    session.add(
        User(
            username=RELEASE_DEFAULT_ADMIN_USER,
            password_hash=hash_password(RELEASE_DEFAULT_ADMIN_PASSWORD),
            full_name=RELEASE_DEFAULT_ADMIN_FULL_NAME,
            role="admin",
            created_date=str(date.today()),
        )
    )
    _mark_default_admin_seeded(session)
    session.commit()


def _users_to_dataframe(users):
    user_columns = ["username", "password_hash", "full_name", "role", "created_date"]
    data = []
    for user in users:
        data.append(
            {
                "username": user.username,
                "password_hash": user.password_hash,
                "full_name": user.full_name,
                "role": user.role,
                "created_date": user.created_date,
            }
        )
    return pd.DataFrame(data, columns=user_columns).fillna("")


def check_users():
    session = SessionLocal()
    try:
        _ensure_release_default_admin(session)
        users = session.query(User).all()
        if not users:
            _bootstrap_admin_if_enabled(session)
            users = session.query(User).all()
        return _users_to_dataframe(users)
    finally:
        session.close()


def list_visible_users(actor_username, actor_role):
    session = SessionLocal()
    try:
        query = session.query(User)
        if str(actor_role or "").strip() != "admin":
            query = query.filter_by(username=_norm_text(actor_username))
        return _users_to_dataframe(query.all())
    finally:
        session.close()


def save_users_data(df):
    session = SessionLocal()
    try:
        if df is None:
            return
        for _, row in df.iterrows():
            username = _norm_text(row.get("username"))
            if not username:
                continue

            existing = session.query(User).filter_by(username=username).first()
            if existing:
                existing.password_hash = _norm_text(row.get("password_hash")) or existing.password_hash
                existing.full_name = _norm_text(row.get("full_name"))
                existing.role = _norm_text(row.get("role"))
                created = _norm_text(row.get("created_date"))
                if created:
                    existing.created_date = created
                continue

            session.add(
                User(
                    username=username,
                    password_hash=_norm_text(row.get("password_hash")),
                    full_name=_norm_text(row.get("full_name")),
                    role=_norm_text(row.get("role")),
                    created_date=_norm_text(row.get("created_date")) or str(date.today()),
                )
            )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_user_password_hash(username, password_hash):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False
        user.password_hash = password_hash
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def create_user(username, full_name, password, role):
    username = _norm_text(username)
    full_name = _norm_text(full_name)
    password = str(password or "").strip()
    role = _norm_text(role) or "user"
    if not username or not full_name or not password:
        return False, "يرجى إدخال جميع البيانات"
    if role not in USER_ALLOWED_ROLES:
        return False, "الصلاحية غير صحيحة"

    session = SessionLocal()
    try:
        if session.query(User).filter_by(username=username).first():
            return False, "اسم المستخدم موجود بالفعل"
        session.add(
            User(
                username=username,
                password_hash=hash_password(password),
                full_name=full_name,
                role=role,
                created_date=str(date.today()),
            )
        )
        session.commit()
        return True, "تمت إضافة المستخدم بنجاح"
    except Exception:
        session.rollback()
        return False, "حدث خطأ أثناء إضافة المستخدم"
    finally:
        session.close()


def admin_update_user(target_username, new_username, full_name, role, password=None):
    target_username = _norm_text(target_username)
    new_username = _norm_text(new_username)
    full_name = _norm_text(full_name)
    password = str(password or "").strip()
    role = _norm_text(role) or "user"
    if not target_username or not new_username or not full_name:
        return False, "يرجى إدخال جميع البيانات", None
    if role not in USER_ALLOWED_ROLES:
        return False, "الصلاحية غير صحيحة", None

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=target_username).first()
        if not user:
            return False, "المستخدم غير موجود", None
        if new_username != target_username and session.query(User).filter_by(username=new_username).first():
            return False, "اسم المستخدم موجود بالفعل", None
        user.username = new_username
        user.full_name = full_name
        user.role = role
        if password:
            user.password_hash = hash_password(password)
        session.commit()
        return True, "تم تعديل المستخدم بنجاح", new_username
    except Exception:
        session.rollback()
        return False, "حدث خطأ أثناء تعديل المستخدم", None
    finally:
        session.close()


def update_own_profile(current_username, full_name, password=None):
    current_username = _norm_text(current_username)
    full_name = _norm_text(full_name)
    password = str(password or "").strip()
    if not current_username or not full_name:
        return False, "يرجى إدخال الاسم", None

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=current_username).first()
        if not user:
            return False, "المستخدم غير موجود", None
        user.full_name = full_name
        if password:
            user.password_hash = hash_password(password)
        session.commit()
        return True, "تم تحديث بيانات الحساب بنجاح", user.username
    except Exception:
        session.rollback()
        return False, "حدث خطأ أثناء تحديث الحساب", None
    finally:
        session.close()
