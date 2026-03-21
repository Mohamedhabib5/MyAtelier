from datetime import date
import time

from models import Booking, Payment, SessionLocal


def add_payment(
    booking_id,
    amount,
    bride_name,
    groom_name,
    notes,
    date_val=None,
    session=None,
    commit=True,
    *,
    money_fn,
    money_float_fn,
    msg_invalid_value,
    msg_payment_gt_remaining,
):
    local_session = session is None
    if local_session:
        session = SessionLocal()
    try:
        b = session.query(Booking).filter_by(booking_id=booking_id).first()
        if not b:
            return False, "Booking not found"

        amt = money_fn(amount)
        if amt <= 0:
            return False, msg_invalid_value

        if amt > money_fn(b.remaining):
            return False, msg_payment_gt_remaining

        b.paid = money_float_fn(money_fn(b.paid) + amt)
        b.remaining = money_float_fn(money_fn(b.remaining) - amt)

        pid = f"PAY-{int(time.time()*1000)}"
        p = Payment(
            payment_id=pid,
            payment_date=str(date_val or date.today()),
            booking_id=booking_id,
            amount=money_float_fn(amt),
            customer_name=bride_name,
            groom_name=groom_name,
            remaining_after=money_float_fn(b.remaining),
            notes=notes,
        )
        session.add(p)
        if commit:
            session.commit()
        else:
            session.flush()
        return True, "Payment Added"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        if local_session:
            session.close()


def update_payment(
    p_id,
    booking_id,
    amount,
    notes,
    date_val=None,
    *,
    money_fn,
    money_float_fn,
    msg_invalid_value,
    msg_payment_gt_remaining,
):
    session = SessionLocal()
    try:
        p = session.query(Payment).filter_by(payment_id=p_id).first()
        if not p:
            return False, "Not Found"

        new_amount = money_fn(amount)
        if new_amount <= 0:
            return False, msg_invalid_value

        old_booking_id = p.booking_id
        old_amount = money_fn(p.amount)
        if booking_id != old_booking_id:
            old_b = session.query(Booking).filter_by(booking_id=old_booking_id).first()
            if old_b:
                old_b.paid = money_float_fn(money_fn(old_b.paid) - old_amount)
                old_b.remaining = money_float_fn(money_fn(old_b.remaining) + old_amount)

            new_b = session.query(Booking).filter_by(booking_id=booking_id).first()
            if not new_b:
                session.rollback()
                return False, "Booking not found"
            if new_amount > money_fn(new_b.remaining):
                session.rollback()
                return False, msg_payment_gt_remaining
            new_b.paid = money_float_fn(money_fn(new_b.paid) + new_amount)
            new_b.remaining = money_float_fn(money_fn(new_b.remaining) - new_amount)
            p.booking_id = booking_id
            p.remaining_after = money_float_fn(new_b.remaining)
        else:
            b = session.query(Booking).filter_by(booking_id=booking_id).first()
            if not b:
                session.rollback()
                return False, "Booking not found"
            new_remaining = money_fn(b.remaining) + old_amount - new_amount
            if new_remaining < 0:
                session.rollback()
                return False, msg_payment_gt_remaining
            b.paid = money_float_fn(money_fn(b.paid) - old_amount + new_amount)
            b.remaining = money_float_fn(new_remaining)
            p.remaining_after = money_float_fn(new_remaining)

        p.amount = money_float_fn(new_amount)
        p.notes = notes
        if date_val:
            p.payment_date = str(date_val)
        session.commit()
        return True, "Updated"
    finally:
        session.close()


def delete_payment(p_id, *, money_fn, money_float_fn):
    session = SessionLocal()
    try:
        p = session.query(Payment).filter_by(payment_id=p_id).first()
        if p:
            b = session.query(Booking).filter_by(booking_id=p.booking_id).first()
            if b:
                p_amount = money_fn(p.amount)
                b.paid = money_float_fn(money_fn(b.paid) - p_amount)
                b.remaining = money_float_fn(money_fn(b.remaining) + p_amount)

            session.delete(p)
            session.commit()
            return True
        return False
    finally:
        session.close()

