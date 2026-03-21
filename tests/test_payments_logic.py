from sqlalchemy.orm import sessionmaker

import logic
from models import Booking


def _patch_logic_sessionlocal(monkeypatch, db_session):
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_session.bind,
    )
    monkeypatch.setattr(logic, "SessionLocal", testing_session_local)


def _create_booking(monkeypatch, db_session, *, price=100.0, paid=0.0):
    _patch_logic_sessionlocal(monkeypatch, db_session)
    ok, msg, booking_id = logic.add_booking(
        customer_name="Payment Test Bride",
        dept=logic.DEPT_MAKEUP,
        service="Service A",
        dress_code="-",
        event_date="2026-03-15",
        price=price,
        paid=paid,
        notes="",
        reg_date="2026-03-05",
    )
    assert ok is True, msg
    assert booking_id is not None
    return booking_id


def test_add_booking_rejects_paid_greater_than_price(monkeypatch, db_session):
    _patch_logic_sessionlocal(monkeypatch, db_session)
    ok, msg, booking_id = logic.add_booking(
        customer_name="Overpay Bride",
        dept=logic.DEPT_MAKEUP,
        service="Service A",
        dress_code="-",
        event_date="2026-03-15",
        price=100.0,
        paid=150.0,
        notes="",
        reg_date="2026-03-05",
    )
    assert ok is False
    assert msg == logic.MSG_PAID_GT_PRICE
    assert booking_id is None


def test_add_payment_rejects_greater_than_remaining(monkeypatch, db_session):
    booking_id = _create_booking(monkeypatch, db_session, price=200.0, paid=0.0)

    ok, msg = logic.add_payment(
        booking_id=booking_id,
        amount=250.0,
        bride_name="Payment Test Bride",
        groom_name="",
        notes="",
        date_val="2026-03-05",
    )
    assert ok is False
    assert msg == logic.MSG_PAYMENT_GT_REMAINING


def test_add_payment_updates_paid_and_remaining(monkeypatch, db_session):
    booking_id = _create_booking(monkeypatch, db_session, price=200.0, paid=0.0)

    ok, msg = logic.add_payment(
        booking_id=booking_id,
        amount=75.0,
        bride_name="Payment Test Bride",
        groom_name="",
        notes="Unit test payment",
        date_val="2026-03-05",
    )
    assert ok is True, msg

    row = db_session.query(Booking).filter_by(booking_id=booking_id).first()
    assert row is not None
    assert float(row.paid) == 75.0
    assert float(row.remaining) == 125.0

