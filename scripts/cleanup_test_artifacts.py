from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models import SessionLocal, Booking, Payment


CUSTOMER_MARKERS = ("E2E ", "Integration Bride", "Payment Test Bride")
SERVICE_MARKERS = ("E2E ",)
BOOKING_ID_MARKERS = ("MK-", "PH-", "HR-", "SK-", "DR-", "GEN-")
LEGACY_SERVICE_MARKERS = ("Integration Service", "Service A")


def _matches_markers(value: str, markers: tuple[str, ...]) -> bool:
    text = str(value or "").strip()
    return any(text.startswith(m) or text == m for m in markers)


def collect_target_booking_ids(session, include_legacy: bool = False) -> set[str]:
    target_ids: set[str] = set()
    for b in session.query(Booking).all():
        booking_id = str(b.booking_id or "").strip()
        customer_hit = _matches_markers(b.customer_name, CUSTOMER_MARKERS)
        service_hit = _matches_markers(b.service, SERVICE_MARKERS)
        id_shape_ok = _matches_markers(booking_id, BOOKING_ID_MARKERS)
        legacy_service_hit = include_legacy and _matches_markers(b.service, LEGACY_SERVICE_MARKERS)

        if id_shape_ok and (customer_hit or service_hit or legacy_service_hit):
            target_ids.add(str(b.booking_id))
    return target_ids


def run_cleanup(apply: bool, include_legacy: bool = False) -> int:
    session = SessionLocal()
    try:
        target_ids = collect_target_booking_ids(session, include_legacy=include_legacy)
        if not target_ids:
            print("No matching test artifact bookings found.")
            return 0

        payments = session.query(Payment).filter(Payment.booking_id.in_(list(target_ids))).all()
        bookings = session.query(Booking).filter(Booking.booking_id.in_(list(target_ids))).all()

        print(f"Matched bookings: {len(bookings)}")
        print(f"Matched linked payments: {len(payments)}")

        if not apply:
            print("Dry run only. Re-run with --apply to delete.")
            return 0

        for p in payments:
            session.delete(p)
        for b in bookings:
            session.delete(b)
        session.commit()
        print("Cleanup applied successfully.")
        return 0
    except Exception as exc:
        session.rollback()
        print(f"Cleanup failed: {exc}")
        return 1
    finally:
        session.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Find and optionally delete test artifact bookings/payments.")
    parser.add_argument("--apply", action="store_true", help="Delete matched rows. Default is dry run.")
    parser.add_argument(
        "--include-legacy",
        action="store_true",
        help="Also match legacy broad service markers (Integration Service / Service A).",
    )
    args = parser.parse_args()
    return run_cleanup(apply=args.apply, include_legacy=args.include_legacy)


if __name__ == "__main__":
    raise SystemExit(main())
