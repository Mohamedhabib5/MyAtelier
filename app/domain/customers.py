from datetime import date

from models import Booking, Customer, SessionLocal


def _norm_text(val):
    if val is None:
        return ""
    return str(val).replace("\u00A0", " ").strip()


def add_customer(
    name,
    groom,
    phone1,
    phone2,
    address,
    reg_date=None,
    notes="",
    *,
    msg_missing_info="",
    msg_invalid_phone="",
    msg_added="",
):
    if not name or not groom or not phone1 or not address:
        return False, msg_missing_info, None
    if not (phone1.isdigit() and len(phone1) >= 10):
        return False, msg_invalid_phone, None

    session = SessionLocal()
    try:
        if session.query(Customer).filter_by(phone1=phone1).first():
            return False, "\u26a0\ufe0f \u0647\u0630\u0627 \u0627\u0644\u0639\u0645\u064a\u0644 \u0645\u0633\u062c\u0644 \u0628\u0627\u0644\u0641\u0639\u0644 (\u0627\u0644\u0647\u0627\u062a\u0641 \u0645\u0643\u0631\u0631)", None

        last = session.query(Customer).all()
        max_id = 100
        for c in last:
            try:
                curr = int(c.customer_id.replace("C-", ""))
                if curr > max_id:
                    max_id = curr
            except Exception:
                pass
        new_id = f"C-{max_id + 1}"

        c = Customer(
            customer_id=new_id,
            reg_date=str(reg_date) if reg_date else str(date.today()),
            name=name,
            groom_name=groom,
            address=address,
            phone1=phone1,
            phone2=phone2,
            notes=notes,
        )
        session.add(c)
        session.commit()
        return True, msg_added, new_id
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}", None
    finally:
        session.close()


def update_customer(
    c_id,
    name,
    groom,
    phone1,
    phone2,
    address,
    reg_date=None,
    notes="",
    *,
    msg_missing_info="",
    msg_not_found="",
    msg_phone_used_by_another="",
    msg_updated="",
):
    if not name or not groom or not phone1:
        return False, msg_missing_info

    session = SessionLocal()
    try:
        c = session.query(Customer).filter_by(customer_id=c_id).first()
        if not c:
            return False, msg_not_found

        exist = session.query(Customer).filter(Customer.phone1 == phone1, Customer.customer_id != c_id).first()
        if exist:
            return False, msg_phone_used_by_another

        old_name = c.name
        c.name = name
        c.groom_name = groom
        c.phone1 = phone1
        c.phone2 = phone2
        c.address = address
        c.notes = notes
        if reg_date:
            c.reg_date = str(reg_date)

        old_norm = _norm_text(old_name)
        new_norm = _norm_text(name)
        if old_norm and old_norm != new_norm:
            for b in session.query(Booking).all():
                if _norm_text(b.customer_name) == old_norm:
                    b.customer_name = name

        session.commit()
        return True, msg_updated
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()


def delete_customer(c_id, *, msg_not_found="", msg_has_bookings="", msg_deleted=""):
    session = SessionLocal()
    try:
        c = session.query(Customer).filter_by(customer_id=c_id).first()
        if not c:
            return False, msg_not_found
        has_booking = bool(session.query(Booking).filter_by(customer_id=c_id).first())
        if not has_booking:
            target_name = _norm_text(c.name)
            for row in session.query(Booking.customer_name).all():
                if _norm_text(row[0]) == target_name:
                    has_booking = True
                    break
        if has_booking:
            return False, msg_has_bookings

        session.delete(c)
        session.commit()
        return True, msg_deleted
    finally:
        session.close()

