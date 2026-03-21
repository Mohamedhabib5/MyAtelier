import pandas as pd

from models import AppSetting, Booking, Department, Service, SessionLocal


def get_app_setting(key, default_value=""):
    session = SessionLocal()
    try:
        row = session.query(AppSetting).filter_by(key=key).first()
        if not row or row.value is None:
            return default_value
        return str(row.value)
    finally:
        session.close()


def set_app_setting(key, value):
    session = SessionLocal()
    try:
        row = session.query(AppSetting).filter_by(key=key).first()
        if row:
            row.value = str(value)
        else:
            session.add(AppSetting(key=key, value=str(value)))
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def set_company_name(name, *, norm_text_fn, set_app_setting_fn):
    clean_name = norm_text_fn(name)
    if not clean_name:
        return False, "اسم الشركه مطلوب", None
    if len(clean_name) > 80:
        return False, "اسم الشركه طويل جدا", None
    if not set_app_setting_fn("company_name", clean_name):
        return False, "حدث خطأ أثناء الحفظ", None
    return True, "تم حفظ اسم الشركه", clean_name


def check_departments(default_departments):
    session = SessionLocal()
    try:
        depts = session.query(Department).all()
        if not depts:
            for d in default_departments:
                session.add(Department(department_name=d))
            session.commit()
            depts = session.query(Department).all()
        return pd.DataFrame([{"department_name": d.department_name} for d in depts])
    finally:
        session.close()


def add_department(name, *, msg_missing_info="", msg_already_exists="", msg_added=""):
    session = SessionLocal()
    try:
        if not name:
            return False, msg_missing_info
        if session.query(Department).filter_by(department_name=name).first():
            return False, msg_already_exists
        session.add(Department(department_name=name))
        session.commit()
        return True, msg_added
    finally:
        session.close()


def update_department(old_name, new_name, *, msg_not_found="", msg_already_exists="", msg_updated=""):
    session = SessionLocal()
    try:
        dept = session.query(Department).filter_by(department_name=old_name).first()
        if not dept:
            return False, msg_not_found
        if old_name != new_name and session.query(Department).filter_by(department_name=new_name).first():
            return False, msg_already_exists
        dept.department_name = new_name
        session.commit()
        return True, msg_updated
    finally:
        session.close()


def delete_department(name, *, msg_not_found="", msg_in_use="", msg_deleted=""):
    session = SessionLocal()
    try:
        dept = session.query(Department).filter_by(department_name=name).first()
        if not dept:
            return False, msg_not_found
        has_services = session.query(Service).filter_by(department=name).first()
        has_bookings = session.query(Booking).filter_by(department=name).first()
        if has_services or has_bookings:
            return False, msg_in_use
        session.delete(dept)
        session.commit()
        return True, msg_deleted
    finally:
        session.close()

