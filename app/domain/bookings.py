from datetime import date
import time

from models import Booking, Payment, SessionLocal


def _norm_text(val):
    if val is None:
        return ""
    return str(val).replace("\u00A0", " ").strip()


def _norm_code(val):
    return "".join(_norm_text(val).split())


def add_booking(
    customer_name,
    dept,
    service,
    dress_code,
    event_date,
    price,
    paid,
    status,
    notes="",
    reg_date=None,
    *,
    canonical_department_fn,
    find_customer_fn,
    find_service_fn,
    is_no_dress_fn,
    money_fn,
    money_float_fn,
    add_payment_fn,
    dept_map,
    booking_status_active,
    note_booking_downpay,
    msg_dress_booked_same_date,
    msg_invalid_value,
    msg_paid_gt_price,
):
    session = SessionLocal()
    try:
        dept_name = canonical_department_fn(session, dept)
        customer_obj = find_customer_fn(session, customer_name)
        customer_id = customer_obj.customer_id if customer_obj else None
        customer_display_name = customer_obj.name if customer_obj else customer_name
        service_obj = find_service_fn(session, service, dept=dept_name)
        service_display_name = service_obj.name if service_obj else service
        service_id = service_obj.service_id if service_obj else None

        dress_code_norm = _norm_text(dress_code)
        if not is_no_dress_fn(dress_code_norm):
            target = _norm_code(dress_code_norm)
            if target:
                event_str = str(event_date)
                for code, _ev in session.query(Booking.dress_code, Booking.event_date).filter(Booking.event_date == event_str).all():
                    if _norm_code(code) == target:
                        return False, msg_dress_booked_same_date, None

        prefix = dept_map.get(dept_name, "GEN")
        bid = f"{prefix}-{int(time.time()*1000)}"

        total_price = money_fn(price)
        initial_paid = money_fn(paid)
        if total_price < 0 or initial_paid < 0:
            return False, msg_invalid_value, None
        if initial_paid > total_price:
            return False, msg_paid_gt_price, None

        status_val = _norm_text(status) or booking_status_active

        b = Booking(
            booking_id=bid,
            booking_date=str(reg_date or date.today()),
            customer_name=customer_display_name,
            customer_id=customer_id,
            department=dept_name,
            service_id=service_id,
            service=service_display_name,
            dress_code=dress_code_norm,
            event_date=str(event_date),
            price=money_float_fn(total_price),
            paid=0.0,
            remaining=money_float_fn(total_price),
            status=status_val,
            notes=notes,
        )
        session.add(b)
        session.flush()

        if initial_paid > 0:
            groom = customer_obj.groom_name if customer_obj else ""
            ok, msg = add_payment_fn(
                bid,
                money_float_fn(initial_paid),
                customer_display_name,
                groom,
                note_booking_downpay,
                str(reg_date or date.today()),
                session=session,
                commit=False,
            )
            if not ok:
                session.rollback()
                return False, msg, None

        session.commit()
        return True, "Booked", bid
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}", None
    finally:
        session.close()


def update_booking(
    b_id,
    customer_name,
    dept,
    service,
    dress_code,
    event_date,
    price,
    paid,
    status,
    notes,
    *,
    canonical_department_fn,
    find_customer_fn,
    find_service_fn,
    is_no_dress_fn,
    money_fn,
    money_float_fn,
    booking_status_active,
    msg_dress_booked_same_date,
    msg_invalid_value,
    msg_paid_gt_price,
):
    session = SessionLocal()
    try:
        b = session.query(Booking).filter_by(booking_id=b_id).first()
        if not b:
            return False, "Not Found"
        dept_name = canonical_department_fn(session, dept)
        customer_obj = find_customer_fn(session, customer_name)
        customer_id = customer_obj.customer_id if customer_obj else None
        customer_display_name = customer_obj.name if customer_obj else customer_name
        service_obj = find_service_fn(session, service, dept=dept_name)
        service_display_name = service_obj.name if service_obj else service
        service_id = service_obj.service_id if service_obj else None

        dress_code_norm = _norm_text(dress_code)
        if not is_no_dress_fn(dress_code_norm):
            changed = _norm_code(b.dress_code) != _norm_code(dress_code_norm) or str(b.event_date) != str(event_date)
            if changed:
                target = _norm_code(dress_code_norm)
                if target:
                    event_str = str(event_date)
                    for code, _ev, bid in session.query(Booking.dress_code, Booking.event_date, Booking.booking_id).filter(Booking.event_date == event_str).all():
                        if bid != b_id and _norm_code(code) == target:
                            return False, msg_dress_booked_same_date

        total_price = money_fn(price)
        total_paid = money_fn(paid)
        if total_price < 0 or total_paid < 0:
            return False, msg_invalid_value
        if total_paid > total_price:
            return False, msg_paid_gt_price

        b.customer_name = customer_display_name
        b.customer_id = customer_id
        b.department = dept_name
        b.service_id = service_id
        b.service = service_display_name
        b.dress_code = dress_code_norm
        b.event_date = str(event_date)
        b.price = money_float_fn(total_price)
        b.paid = money_float_fn(total_paid)
        b.remaining = money_float_fn(total_price - total_paid)
        b.status = _norm_text(status) or booking_status_active
        b.notes = notes
        session.commit()
        return True, "Updated"
    finally:
        session.close()


def delete_booking(b_id):
    session = SessionLocal()
    try:
        b = session.query(Booking).filter_by(booking_id=b_id).first()
        if not b:
            return False, "Not Found"
        has_payment = session.query(Payment).filter_by(booking_id=b_id).first()
        if has_payment:
            return False, "Has Payments"
        session.delete(b)
        session.commit()
        return True, "Deleted"
    finally:
        session.close()

