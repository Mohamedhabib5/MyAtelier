from models import Customer, Department, Service


def _norm_text(val):
    if val is None:
        return ""
    return str(val).replace("\u00A0", " ").strip()


def _norm_code(val):
    return "".join(_norm_text(val).split())


def is_dresses_dept(val, dept_dresses):
    d = _norm_text(val)
    if not d:
        return False
    return _norm_code(d) in {_norm_code(dept_dresses)}


def is_no_dress(val, no_dress_label):
    v = _norm_text(val)
    return v in ("", "-", no_dress_label)


def find_customer_by_name_or_id(session, customer_name):
    target_name = _norm_text(customer_name)
    if not target_name:
        return None
    for c in session.query(Customer).all():
        if _norm_text(c.name) == target_name:
            return c
    return session.query(Customer).filter_by(customer_id=target_name).first()


def find_service_by_name_or_id(session, service_value, dept=None):
    target = _norm_text(service_value)
    if not target:
        return None

    dept_norm = _norm_text(dept)
    services = session.query(Service).all()

    preferred = []
    fallback = []
    for s in services:
        pool = preferred if (not dept_norm or _norm_text(s.department) == dept_norm) else fallback
        if _norm_text(s.name) == target or _norm_text(s.service_id) == target:
            pool.append(s)

    if preferred:
        return preferred[0]
    if fallback:
        return fallback[0]
    return None


def find_department_by_name(session, dept_value):
    target = _norm_text(dept_value)
    if not target:
        return None
    for d in session.query(Department).all():
        if _norm_text(d.department_name) == target:
            return d
    return None


def canonical_department_name(session, dept_value):
    d = find_department_by_name(session, dept_value)
    if d:
        return d.department_name
    return dept_value


def ensure_unknown_department(session):
    unknown = find_department_by_name(session, "UNKNOWN")
    if unknown:
        return unknown.department_name
    session.add(Department(department_name="UNKNOWN"))
    session.commit()
    return "UNKNOWN"

