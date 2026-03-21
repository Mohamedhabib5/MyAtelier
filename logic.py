from sqlalchemy import text
from models import engine, init_db, SessionLocal, Department, Customer, Service, Dress, Booking, Payment, AppSetting
from app.constants import (
    DEFAULT_COMPANY_NAME,
    IMAGE_FOLDER,
    DEPT_MAKEUP,
    DEPT_PHOTO,
    DEPT_HAIR,
    DEPT_SKIN,
    DEPT_DRESSES,
    NO_DRESS_LABEL,
    NOTE_BOOKING_DOWNPAY,
    MSG_DRESS_BOOKED_SAME_DATE,
    MSG_INVALID_VALUE,
    MSG_PAID_GT_PRICE,
    MSG_PAYMENT_GT_REMAINING,
    MSG_MISSING_INFO,
    MSG_ALREADY_EXISTS,
    MSG_NOT_FOUND,
    MSG_IN_USE,
    MSG_ADDED,
    MSG_UPDATED,
    MSG_DELETED,
    MSG_INVALID_PHONE,
    MSG_PHONE_USED_BY_ANOTHER,
    MSG_HAS_BOOKINGS,
    MSG_CODE_EXISTS,
    MSG_NEW_CODE_EXISTS,
    BOOKING_STATUS_ACTIVE,
)
from app.domain.formatting import (
    format_date_ddmmyyyy as _domain_format_date_ddmmyyyy,
    money as _domain_money,
    money_float as _domain_money_float,
    norm_text as _domain_norm_text,
    norm_code as _domain_norm_code,
)
from app.domain import auth as auth_domain
from app.domain import customers as customers_domain
from app.domain import services as services_domain
from app.domain import dresses as dresses_domain
from app.domain import bookings as bookings_domain
from app.domain import payments as payments_domain
from app.domain import settings_departments as settings_dept_domain
from app.domain import resolvers as resolvers_domain
from app.domain import migrations as migrations_domain
from app.domain import data_access as data_access_domain
from app.domain import (
    departments_facade as departments_facade_domain,
    customers_facade as customers_facade_domain,
    services_facade as services_facade_domain,
    dresses_facade as dresses_facade_domain,
    bookings_facade as bookings_facade_domain,
    payments_facade as payments_facade_domain,
)
from app.domain import logic_departments_api as logic_departments_api_domain
from app.domain import logic_customers_api as logic_customers_api_domain
from app.domain import logic_services_api as logic_services_api_domain
from app.domain import logic_dresses_api as logic_dresses_api_domain
from app.domain import logic_bookings_api as logic_bookings_api_domain
from app.domain import logic_payments_api as logic_payments_api_domain
from app.domain import logic_settings_api as logic_settings_api_domain
from app.domain import logic_init_api as logic_init_api_domain
from app.domain import logic_auth_api as logic_auth_api_domain
from app.domain import logic_cache_api as logic_cache_api_domain
import os
from functools import partial
from datetime import date

# Kept as compatibility exports for scripts importing logic._norm_text/_norm_code.
_norm_text = _domain_norm_text
_norm_code = _domain_norm_code
format_date_ddmmyyyy = _domain_format_date_ddmmyyyy


def _sync_domain_sessionlocal():
    # Keep test monkeypatching compatible: domain modules should use logic.SessionLocal.
    auth_domain.SessionLocal = SessionLocal
    customers_domain.SessionLocal = SessionLocal
    services_domain.SessionLocal = SessionLocal
    dresses_domain.SessionLocal = SessionLocal
    bookings_domain.SessionLocal = SessionLocal
    payments_domain.SessionLocal = SessionLocal
    settings_dept_domain.SessionLocal = SessionLocal
    migrations_domain.SessionLocal = SessionLocal
    data_access_domain.SessionLocal = SessionLocal


def _with_synced_sessionlocal(fn, *args, **kwargs):
    _sync_domain_sessionlocal()
    return fn(*args, **kwargs)


def _make_synced_wrapper(fn):
    return lambda *args, **kwargs: _with_synced_sessionlocal(fn, *args, **kwargs)


(
    invalidate_data_cache,
    get_data_cache_stats,
    reset_data_cache_stats,
) = logic_cache_api_domain.build_cache_wrappers(_make_synced_wrapper, data_access_domain)


_invalidate_after_write = lambda result, file_name=None: logic_cache_api_domain.invalidate_after_write(
    _with_synced_sessionlocal,
    data_access_domain,
    invalidate_data_cache,
    result,
    file_name=file_name,
)
_invalidate_many = lambda file_names: logic_cache_api_domain.invalidate_many(
    _with_synced_sessionlocal,
    data_access_domain,
    invalidate_data_cache,
    file_names,
)


# --- Settings/Company Facade ---
get_app_setting = _make_synced_wrapper(settings_dept_domain.get_app_setting)
set_app_setting = _make_synced_wrapper(settings_dept_domain.set_app_setting)


get_company_name = lambda: logic_settings_api_domain.get_company_name(
    get_app_setting,
    DEFAULT_COMPANY_NAME,
)


set_company_name = lambda name: logic_settings_api_domain.set_company_name(
    _with_synced_sessionlocal,
    settings_dept_domain,
    set_app_setting,
    _norm_text,
    name,
)


# --- Resolver Facade ---
_is_dresses_dept = partial(resolvers_domain.is_dresses_dept, dept_dresses=DEPT_DRESSES)
_is_no_dress = partial(resolvers_domain.is_no_dress, no_dress_label=NO_DRESS_LABEL)
BOOKING_DEPT_MAP = {
    DEPT_MAKEUP: "MK",
    DEPT_PHOTO: "PH",
    DEPT_HAIR: "HR",
    DEPT_SKIN: "SK",
    DEPT_DRESSES: "DR",
}


# --- Migration/Backfill Facade ---
_ensure_booking_service_id_column = lambda: _with_synced_sessionlocal(
    migrations_domain.ensure_booking_service_id_column, engine
)
_ensure_booking_status_column = lambda: _with_synced_sessionlocal(
    migrations_domain.ensure_booking_status_column, engine, BOOKING_STATUS_ACTIVE
)
_migrate_sqlite_money_columns_to_numeric = lambda: _with_synced_sessionlocal(
    migrations_domain.migrate_sqlite_money_columns_to_numeric, engine
)


_backfill_booking_service_ids = lambda: _with_synced_sessionlocal(
    migrations_domain.backfill_booking_service_ids, resolvers_domain.find_service_by_name_or_id
)
_backfill_service_departments = lambda: _with_synced_sessionlocal(
    migrations_domain.backfill_service_departments, _norm_text, resolvers_domain.ensure_unknown_department
)
_backfill_booking_departments = lambda: _with_synced_sessionlocal(
    migrations_domain.backfill_booking_departments,
    _norm_text, resolvers_domain.ensure_unknown_department, resolvers_domain.find_service_by_name_or_id
)

_money = _domain_money
_money_float = _domain_money_float


_normalize_money_precision = lambda: _with_synced_sessionlocal(
    migrations_domain.normalize_money_precision, _money_float
)


# --- Data Access Facade ---
# Exported column maps/constants (re-exported for compatibility).
C_COLS_MAP, S_COLS_MAP, D_COLS_MAP, B_COLS_MAP, P_COLS_MAP = (
    data_access_domain.C_COLS_MAP,
    data_access_domain.S_COLS_MAP,
    data_access_domain.D_COLS_MAP,
    data_access_domain.B_COLS_MAP,
    data_access_domain.P_COLS_MAP,
)
C_COLS, S_COLS, D_COLS, B_COLS, P_COLS = (
    data_access_domain.C_COLS,
    data_access_domain.S_COLS,
    data_access_domain.D_COLS,
    data_access_domain.B_COLS,
    data_access_domain.P_COLS,
)

# --- Initialization ---
def init_folders():
    return logic_init_api_domain.init_folders(
        os_module=os,
        image_folder=IMAGE_FOLDER,
        init_db_fn=init_db,
        ensure_booking_service_id_column_fn=_ensure_booking_service_id_column,
        migrate_money_columns_fn=_migrate_sqlite_money_columns_to_numeric,
        ensure_booking_status_column_fn=_ensure_booking_status_column,
        backfill_booking_service_ids_fn=_backfill_booking_service_ids,
        backfill_service_departments_fn=_backfill_service_departments,
        backfill_booking_departments_fn=_backfill_booking_departments,
        normalize_money_precision_fn=_normalize_money_precision,
        session_local=SessionLocal,
        ensure_release_default_admin_fn=_ensure_release_default_admin,
    )

# --- Auth/Users (domain wrappers) ---
PBKDF2_ALGO = auth_domain.PBKDF2_ALGO
PBKDF2_ITERATIONS = auth_domain.PBKDF2_ITERATIONS
RELEASE_DEFAULT_ADMIN_USER = auth_domain.RELEASE_DEFAULT_ADMIN_USER
RELEASE_DEFAULT_ADMIN_PASSWORD = auth_domain.RELEASE_DEFAULT_ADMIN_PASSWORD
RELEASE_DEFAULT_ADMIN_FULL_NAME = auth_domain.RELEASE_DEFAULT_ADMIN_FULL_NAME

# Keep legacy symbol exports but avoid redundant pass-through function bodies.
_hash_password_legacy_sha256 = auth_domain._hash_password_legacy_sha256
_hash_password_pbkdf2 = auth_domain._hash_password_pbkdf2
hash_password = auth_domain.hash_password
verify_password = auth_domain.verify_password
_is_strong_bootstrap_password = auth_domain._is_strong_bootstrap_password
_bootstrap_admin_if_enabled = auth_domain._bootstrap_admin_if_enabled
_ensure_release_default_admin = auth_domain._ensure_release_default_admin


(
    check_users,
    save_users_data,
    update_user_password_hash,
    list_visible_users,
    create_user,
    admin_update_user,
    update_own_profile,
) = logic_auth_api_domain.build_user_wrappers(_make_synced_wrapper, auth_domain)


# --- CRUD Facade ---
# Compatibility cache used by UI grid composition.
DATA_CACHE = {}

load_data = _make_synced_wrapper(data_access_domain.load_data)

def check_departments():
    return logic_departments_api_domain.check_departments(
        _with_synced_sessionlocal,
        settings_dept_domain,
        [DEPT_MAKEUP, DEPT_PHOTO, DEPT_DRESSES, DEPT_HAIR, DEPT_SKIN],
    )


def add_department(name):
    return logic_departments_api_domain.add_department(
        departments_facade_domain,
        _with_synced_sessionlocal,
        settings_dept_domain,
        _invalidate_after_write,
        _invalidate_many,
        name=name,
        msg_missing_info=MSG_MISSING_INFO,
        msg_already_exists=MSG_ALREADY_EXISTS,
        msg_added=MSG_ADDED,
    )


def update_department(old_name, new_name):
    return logic_departments_api_domain.update_department(
        departments_facade_domain,
        _with_synced_sessionlocal,
        settings_dept_domain,
        _invalidate_after_write,
        _invalidate_many,
        old_name=old_name,
        new_name=new_name,
        msg_not_found=MSG_NOT_FOUND,
        msg_already_exists=MSG_ALREADY_EXISTS,
        msg_updated=MSG_UPDATED,
    )


def delete_department(name):
    return logic_departments_api_domain.delete_department(
        departments_facade_domain,
        _with_synced_sessionlocal,
        settings_dept_domain,
        _invalidate_after_write,
        _invalidate_many,
        name=name,
        msg_not_found=MSG_NOT_FOUND,
        msg_in_use=MSG_IN_USE,
        msg_deleted=MSG_DELETED,
    )


save_department = lambda name: logic_departments_api_domain.save_department(
    departments_facade_domain,
    add_department,
    name,
)


def add_customer(name, groom, phone1, phone2, address, reg_date=None, notes=""):
    return logic_customers_api_domain.add_customer(
        customers_facade_domain,
        _with_synced_sessionlocal,
        customers_domain,
        _invalidate_after_write,
        name=name,
        groom=groom,
        phone1=phone1,
        phone2=phone2,
        address=address,
        reg_date=reg_date,
        notes=notes,
        msg_missing_info=MSG_MISSING_INFO,
        msg_invalid_phone=MSG_INVALID_PHONE,
        msg_added=MSG_ADDED,
    )


def update_customer(c_id, name, groom, phone1, phone2, address, reg_date=None, notes=""):
    return logic_customers_api_domain.update_customer(
        customers_facade_domain,
        _with_synced_sessionlocal,
        customers_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        c_id=c_id,
        name=name,
        groom=groom,
        phone1=phone1,
        phone2=phone2,
        address=address,
        reg_date=reg_date,
        notes=notes,
        msg_missing_info=MSG_MISSING_INFO,
        msg_not_found=MSG_NOT_FOUND,
        msg_phone_used_by_another=MSG_PHONE_USED_BY_ANOTHER,
        msg_updated=MSG_UPDATED,
    )


def delete_customer(c_id):
    return logic_customers_api_domain.delete_customer(
        customers_facade_domain,
        _with_synced_sessionlocal,
        customers_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        c_id=c_id,
        msg_not_found=MSG_NOT_FOUND,
        msg_has_bookings=MSG_HAS_BOOKINGS,
        msg_deleted=MSG_DELETED,
    )


def add_service(name, dept, price):
    return logic_services_api_domain.add_service(
        services_facade_domain,
        _with_synced_sessionlocal,
        services_domain,
        _invalidate_after_write,
        name=name,
        dept=dept,
        price=price,
        money_float_fn=_money_float,
        msg_missing_info=MSG_MISSING_INFO,
        msg_added=MSG_ADDED,
    )


def update_service(s_id, name, dept, price):
    return logic_services_api_domain.update_service(
        services_facade_domain,
        _with_synced_sessionlocal,
        services_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        s_id=s_id,
        name=name,
        dept=dept,
        price=price,
        money_float_fn=_money_float,
        msg_updated=MSG_UPDATED,
        msg_not_found=MSG_NOT_FOUND,
    )


def delete_service(s_id):
    return logic_services_api_domain.delete_service(
        services_facade_domain,
        _with_synced_sessionlocal,
        services_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        s_id=s_id,
        msg_not_found=MSG_NOT_FOUND,
        msg_has_bookings=MSG_HAS_BOOKINGS,
        msg_deleted=MSG_DELETED,
    )


save_image = lambda image_contents, dress_code: logic_dresses_api_domain.save_image(
    dresses_facade_domain,
    _with_synced_sessionlocal,
    dresses_domain,
    image_contents=image_contents,
    dress_code=dress_code,
    image_folder=IMAGE_FOLDER,
)


def add_dress(code, d_type, date_buy, status, desc, image_contents=None):
    return logic_dresses_api_domain.add_dress(
        dresses_facade_domain,
        _with_synced_sessionlocal,
        dresses_domain,
        _invalidate_after_write,
        code=code,
        d_type=d_type,
        date_buy=date_buy,
        status=status,
        desc=desc,
        image_contents=image_contents,
        image_folder=IMAGE_FOLDER,
        msg_missing_info=MSG_MISSING_INFO,
        msg_code_exists=MSG_CODE_EXISTS,
        msg_added=MSG_ADDED,
    )


def update_dress(old_code, new_code, d_type, date_buy, status, desc, image_contents=None):
    return logic_dresses_api_domain.update_dress(
        dresses_facade_domain,
        _with_synced_sessionlocal,
        dresses_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        old_code=old_code,
        new_code=new_code,
        d_type=d_type,
        date_buy=date_buy,
        status=status,
        desc=desc,
        image_contents=image_contents,
        image_folder=IMAGE_FOLDER,
        msg_not_found=MSG_NOT_FOUND,
        msg_new_code_exists=MSG_NEW_CODE_EXISTS,
        msg_updated=MSG_UPDATED,
    )


def delete_dress(d_code):
    return logic_dresses_api_domain.delete_dress(
        dresses_facade_domain,
        _with_synced_sessionlocal,
        dresses_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        d_code=d_code,
        image_folder=IMAGE_FOLDER,
        msg_not_found=MSG_NOT_FOUND,
        msg_has_bookings=MSG_HAS_BOOKINGS,
        msg_deleted=MSG_DELETED,
    )


def add_booking(customer_name, dept, service, dress_code, event_date, price, paid, status=BOOKING_STATUS_ACTIVE, notes="", reg_date=None):
    return logic_bookings_api_domain.add_booking(
        bookings_facade_domain,
        _with_synced_sessionlocal,
        bookings_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        customer_name=customer_name,
        dept=dept,
        service=service,
        dress_code=dress_code,
        event_date=event_date,
        price=price,
        paid=paid,
        status=status,
        notes=notes,
        reg_date=reg_date,
        canonical_department_fn=resolvers_domain.canonical_department_name,
        find_customer_fn=resolvers_domain.find_customer_by_name_or_id,
        find_service_fn=resolvers_domain.find_service_by_name_or_id,
        is_no_dress_fn=_is_no_dress,
        money_fn=_money,
        money_float_fn=_money_float,
        add_payment_fn=add_payment,
        dept_map=BOOKING_DEPT_MAP,
        booking_status_active=BOOKING_STATUS_ACTIVE,
        note_booking_downpay=NOTE_BOOKING_DOWNPAY,
        msg_dress_booked_same_date=MSG_DRESS_BOOKED_SAME_DATE,
        msg_invalid_value=MSG_INVALID_VALUE,
        msg_paid_gt_price=MSG_PAID_GT_PRICE,
    )

def update_booking(b_id, customer_name, dept, service, dress_code, event_date, price, paid, status, notes):
    return logic_bookings_api_domain.update_booking(
        bookings_facade_domain,
        _with_synced_sessionlocal,
        bookings_domain,
        _invalidate_after_write,
        b_id=b_id,
        customer_name=customer_name,
        dept=dept,
        service=service,
        dress_code=dress_code,
        event_date=event_date,
        price=price,
        paid=paid,
        status=status,
        notes=notes,
        canonical_department_fn=resolvers_domain.canonical_department_name,
        find_customer_fn=resolvers_domain.find_customer_by_name_or_id,
        find_service_fn=resolvers_domain.find_service_by_name_or_id,
        is_no_dress_fn=_is_no_dress,
        money_fn=_money,
        money_float_fn=_money_float,
        booking_status_active=BOOKING_STATUS_ACTIVE,
        msg_dress_booked_same_date=MSG_DRESS_BOOKED_SAME_DATE,
        msg_invalid_value=MSG_INVALID_VALUE,
        msg_paid_gt_price=MSG_PAID_GT_PRICE,
    )

def delete_booking(b_id):
    return logic_bookings_api_domain.delete_booking(
        bookings_facade_domain,
        _with_synced_sessionlocal,
        bookings_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        b_id=b_id,
    )

def add_payment(booking_id, amount, bride_name, groom_name, notes, date_val=None, session=None, commit=True):
    return logic_payments_api_domain.add_payment(
        payments_facade_domain,
        _with_synced_sessionlocal,
        payments_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        booking_id=booking_id,
        amount=amount,
        bride_name=bride_name,
        groom_name=groom_name,
        notes=notes,
        date_val=date_val,
        session=session,
        commit=commit,
        money_fn=_money,
        money_float_fn=_money_float,
        msg_invalid_value=MSG_INVALID_VALUE,
        msg_payment_gt_remaining=MSG_PAYMENT_GT_REMAINING,
    )

def update_payment(p_id, booking_id, amount, notes, date_val=None):
    return logic_payments_api_domain.update_payment(
        payments_facade_domain,
        _with_synced_sessionlocal,
        payments_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        p_id=p_id,
        booking_id=booking_id,
        amount=amount,
        notes=notes,
        date_val=date_val,
        money_fn=_money,
        money_float_fn=_money_float,
        msg_invalid_value=MSG_INVALID_VALUE,
        msg_payment_gt_remaining=MSG_PAYMENT_GT_REMAINING,
    )

def delete_payment(p_id):
    return logic_payments_api_domain.delete_payment(
        payments_facade_domain,
        _with_synced_sessionlocal,
        payments_domain,
        _invalidate_after_write,
        invalidate_data_cache,
        p_id=p_id,
        money_fn=_money,
        money_float_fn=_money_float,
    )



