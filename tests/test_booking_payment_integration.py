from sqlalchemy.orm import sessionmaker

import logic
from models import Booking, Payment


def _patch_logic_sessionlocal(monkeypatch, db_session):
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_session.bind,
    )
    monkeypatch.setattr(logic, "SessionLocal", testing_session_local)


def test_booking_to_payment_link_updates_remaining(monkeypatch, db_session):
    _patch_logic_sessionlocal(monkeypatch, db_session)

    ok, msg, booking_id = logic.add_booking(
        customer_name="Integration Bride",
        dept=logic.DEPT_MAKEUP,
        service="Integration Service",
        dress_code="-",
        event_date="2026-03-20",
        price=300.0,
        paid=0.0,
        status=logic.BOOKING_STATUS_ACTIVE,
        notes="",
        reg_date="2026-03-05",
    )
    assert ok is True, msg
    assert booking_id is not None

    pay_ok, pay_msg = logic.add_payment(
        booking_id=booking_id,
        amount=120.0,
        bride_name="Integration Bride",
        groom_name="",
        notes="Integration payment",
        date_val="2026-03-06",
    )
    assert pay_ok is True, pay_msg

    booking_row = db_session.query(Booking).filter_by(booking_id=booking_id).first()
    payment_row = db_session.query(Payment).filter_by(booking_id=booking_id).first()

    assert booking_row is not None
    assert payment_row is not None
    assert payment_row.booking_id == booking_id
    assert float(booking_row.paid) == 120.0
    assert float(booking_row.remaining) == 180.0
    assert float(payment_row.remaining_after) == 180.0

