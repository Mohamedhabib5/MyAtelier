import re

import logic
from app.domain import auth as auth_domain
from models import AppSetting, User
from sqlalchemy.orm import sessionmaker


def _patch_logic_sessionlocal(monkeypatch, db_session):
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_session.bind,
    )
    monkeypatch.setattr(logic, "SessionLocal", testing_session_local)


def test_hash_password_returns_pbkdf2_format():
    password_hash = logic.hash_password("StrongPass123")
    parts = password_hash.split("$")

    assert len(parts) == 4
    assert parts[0] == logic.PBKDF2_ALGO
    assert parts[1].isdigit()
    assert len(parts[2]) > 0
    assert re.fullmatch(r"[0-9a-f]+", parts[3]) is not None


def test_verify_password_accepts_pbkdf2_and_rejects_wrong_password():
    password_hash = logic.hash_password("StrongPass123")

    assert logic.verify_password("StrongPass123", password_hash) is True
    assert logic.verify_password("WrongPass123", password_hash) is False


def test_verify_password_supports_legacy_sha256_hashes():
    legacy_hash = logic._hash_password_legacy_sha256("LegacyPass123")

    assert logic.verify_password("LegacyPass123", legacy_hash) is True
    assert logic.verify_password("WrongLegacy", legacy_hash) is False


def test_default_admin_seeded_once_without_recreation_after_username_change(db_session):
    auth_domain._ensure_release_default_admin(db_session)

    seeded_user = db_session.query(User).filter_by(username="admin").first()
    assert seeded_user is not None
    assert logic.verify_password("admin123", seeded_user.password_hash) is True

    seeded_user.username = "atelier-admin"
    db_session.commit()

    auth_domain._ensure_release_default_admin(db_session)

    users = db_session.query(User).all()
    usernames = sorted(user.username for user in users)
    marker = db_session.query(AppSetting).filter_by(key=auth_domain.DEFAULT_ADMIN_SEEDED_KEY).first()

    assert usernames == ["atelier-admin"]
    assert marker is not None
    assert marker.value == "1"


def test_list_visible_users_returns_only_self_for_regular_user(monkeypatch, db_session):
    _patch_logic_sessionlocal(monkeypatch, db_session)
    auth_domain._ensure_release_default_admin(db_session)

    ok1, _ = logic.create_user("user1", "User One", "StrongPass123", "user")
    ok2, _ = logic.create_user("user2", "User Two", "StrongPass456", "user")

    assert ok1 is True
    assert ok2 is True

    visible_df = logic.list_visible_users("user1", "user")
    admin_df = logic.list_visible_users("admin", "admin")

    assert visible_df["username"].tolist() == ["user1"]
    assert sorted(admin_df["username"].tolist()) == ["admin", "user1", "user2"]


def test_admin_can_rename_user_and_update_password(monkeypatch, db_session):
    _patch_logic_sessionlocal(monkeypatch, db_session)
    auth_domain._ensure_release_default_admin(db_session)
    ok, _ = logic.create_user("user1", "User One", "StrongPass123", "user")
    assert ok is True

    success, _msg, updated_username = logic.admin_update_user(
        "user1",
        "user1-renamed",
        "User One Updated",
        "user",
        "NewStrongPass123",
    )

    updated_user = db_session.query(User).filter_by(username="user1-renamed").first()

    assert success is True
    assert updated_username == "user1-renamed"
    assert updated_user is not None
    assert updated_user.full_name == "User One Updated"
    assert logic.verify_password("NewStrongPass123", updated_user.password_hash) is True


def test_regular_user_can_update_own_profile_only(monkeypatch, db_session):
    _patch_logic_sessionlocal(monkeypatch, db_session)
    auth_domain._ensure_release_default_admin(db_session)
    ok, _ = logic.create_user("user1", "User One", "StrongPass123", "user")
    assert ok is True

    success, _msg, _username = logic.update_own_profile("user1", "User One Edited", "EditedPass123")
    updated_user = db_session.query(User).filter_by(username="user1").first()

    assert success is True
    assert updated_user is not None
    assert updated_user.full_name == "User One Edited"
    assert logic.verify_password("EditedPass123", updated_user.password_hash) is True
