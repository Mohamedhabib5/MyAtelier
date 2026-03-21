from models import Booking, Department, Service, SessionLocal


def _norm_text(val):
    if val is None:
        return ""
    return str(val).replace("\u00A0", " ").strip()


def _find_department_by_name(session, dept_value):
    target = _norm_text(dept_value)
    if not target:
        return None
    for d in session.query(Department).all():
        if _norm_text(d.department_name) == target:
            return d
    return None


def _canonical_department_name(session, dept_value):
    d = _find_department_by_name(session, dept_value)
    if d:
        return d.department_name
    return dept_value


def add_service(
    name,
    dept,
    price,
    *,
    money_float_fn,
    msg_missing_info="",
    msg_added="",
):
    if not name or not dept:
        return False, msg_missing_info, None

    session = SessionLocal()
    try:
        dept_name = _canonical_department_name(session, dept)
        last = session.query(Service).all()
        max_sid = 100
        for s in last:
            try:
                curr = int(s.service_id.replace("S-", ""))
                if curr > max_sid:
                    max_sid = curr
            except Exception:
                pass
        new_id = f"S-{max_sid+1}"

        s = Service(service_id=new_id, name=name, department=dept_name, price=money_float_fn(price))
        session.add(s)
        session.commit()
        return True, msg_added, new_id
    finally:
        session.close()


def update_service(
    s_id,
    name,
    dept,
    price,
    *,
    money_float_fn,
    msg_updated="",
    msg_not_found="",
):
    session = SessionLocal()
    try:
        s = session.query(Service).filter_by(service_id=s_id).first()
        if s:
            dept_name = _canonical_department_name(session, dept)
            old_name = s.name
            old_id = s.service_id
            s.name = name
            s.department = dept_name
            s.price = money_float_fn(price)

            old_name_norm = _norm_text(old_name)
            old_id_norm = _norm_text(old_id)
            for b in session.query(Booking).all():
                service_norm = _norm_text(b.service)
                if service_norm == old_name_norm or service_norm == old_id_norm:
                    b.service = name

            session.commit()
            return True, msg_updated
        return False, msg_not_found
    finally:
        session.close()


def delete_service(s_id, *, msg_not_found="", msg_has_bookings="", msg_deleted=""):
    session = SessionLocal()
    try:
        s = session.query(Service).filter_by(service_id=s_id).first()
        if not s:
            return False, msg_not_found
        target_name = _norm_text(s.name)
        target_id = _norm_text(s.service_id)
        has_booking = False
        for row in session.query(Booking.service, Booking.service_id).all():
            service_norm = _norm_text(row[0])
            service_id_norm = _norm_text(row[1])
            if (
                service_norm == target_name
                or service_norm == target_id
                or service_id_norm == target_id
            ):
                has_booking = True
                break
        if has_booking:
            return False, msg_has_bookings

        session.delete(s)
        session.commit()
        return True, msg_deleted
    finally:
        session.close()

