from sqlalchemy.orm import sessionmaker

import logic
from models import Booking, Customer


def _patch_logic_sessionlocal(monkeypatch, db_session):
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_session.bind,
    )
    monkeypatch.setattr(logic, "SessionLocal", testing_session_local)


def test_add_customer_success(monkeypatch, db_session):
    _patch_logic_sessionlocal(monkeypatch, db_session)

    ok, _msg, customer_id = logic.add_customer(
        name="Test Bride",
        groom="Test Groom",
        phone1="0123456789",
        phone2="",
        address="Test Address",
    )

    assert ok is True
    assert customer_id is not None
    assert str(customer_id).startswith("C-")

    saved = db_session.query(Customer).filter_by(customer_id=customer_id).first()
    assert saved is not None
    assert saved.name == "Test Bride"
    assert saved.groom_name == "Test Groom"


def test_update_customer_success(monkeypatch, db_session):
    _patch_logic_sessionlocal(monkeypatch, db_session)

    ok, _msg, customer_id = logic.add_customer(
        name="Bride Before",
        groom="Groom Before",
        phone1="0123456790",
        phone2="",
        address="Addr Before",
    )
    assert ok is True

    update_ok, _update_msg = logic.update_customer(
        c_id=customer_id,
        name="Bride After",
        groom="Groom After",
        phone1="0123456791",
        phone2="0123456792",
        address="Addr After",
    )

    assert update_ok is True
    updated = db_session.query(Customer).filter_by(customer_id=customer_id).first()
    assert updated is not None
    assert updated.name == "Bride After"
    assert updated.groom_name == "Groom After"
    assert updated.phone1 == "0123456791"
    assert updated.phone2 == "0123456792"
    assert updated.address == "Addr After"


def test_delete_customer_blocked_when_has_booking(monkeypatch, db_session):
    _patch_logic_sessionlocal(monkeypatch, db_session)

    ok, _msg, customer_id = logic.add_customer(
        name="Bride With Booking",
        groom="Groom With Booking",
        phone1="0123456793",
        phone2="",
        address="Booked Address",
    )
    assert ok is True

    db_session.add(
        Booking(
            booking_id="HR-UNIT-1",
            booking_date="2026-03-05",
            customer_name="Bride With Booking",
            customer_id=customer_id,
            department="المكياج",
            service="خدمة",
            dress_code="-",
            event_date="2026-03-10",
            price=100.0,
            paid=0.0,
            remaining=100.0,
            status=logic.BOOKING_STATUS_ACTIVE,
            notes="",
        )
    )
    db_session.commit()

    delete_ok, delete_msg = logic.delete_customer(customer_id)
    assert delete_ok is False
    assert delete_msg == logic.MSG_HAS_BOOKINGS

