from models import Booking, Department, Payment, Service, SessionLocal


def backfill_booking_service_ids(find_service_fn):
    session = SessionLocal()
    try:
        updated = 0
        for booking in session.query(Booking).all():
            if getattr(booking, "service_id", None):
                continue
            service_obj = find_service_fn(session, booking.service, dept=booking.department)
            if service_obj:
                booking.service_id = service_obj.service_id
                booking.service = service_obj.name
                updated += 1
        if updated:
            session.commit()
    except Exception as exc:
        session.rollback()
        print(f"Backfill warning (booking.service_id): {exc}")
    finally:
        session.close()


def backfill_service_departments(norm_text_fn, ensure_unknown_department_fn):
    session = SessionLocal()
    try:
        departments = session.query(Department).all()
        department_names = {norm_text_fn(dept.department_name): dept.department_name for dept in departments}
        unknown_name = ensure_unknown_department_fn(session)
        department_names[norm_text_fn(unknown_name)] = unknown_name
        updated = 0

        for service in session.query(Service).all():
            current = norm_text_fn(getattr(service, "department", ""))
            if current in department_names:
                continue
            service.department = unknown_name
            updated += 1

        if updated:
            session.commit()
    except Exception as exc:
        session.rollback()
        print(f"Backfill warning (service.department): {exc}")
    finally:
        session.close()


def backfill_booking_departments(norm_text_fn, ensure_unknown_department_fn, find_service_fn):
    session = SessionLocal()
    try:
        departments = session.query(Department).all()
        department_names = {norm_text_fn(dept.department_name): dept.department_name for dept in departments}
        unknown_name = ensure_unknown_department_fn(session)
        department_names[norm_text_fn(unknown_name)] = unknown_name
        updated = 0

        for booking in session.query(Booking).all():
            current_department = norm_text_fn(getattr(booking, "department", ""))
            if current_department in department_names:
                continue

            inferred = None
            service_id = norm_text_fn(getattr(booking, "service_id", ""))
            service_name = norm_text_fn(getattr(booking, "service", ""))

            if service_id:
                service = session.query(Service).filter_by(service_id=service_id).first()
                if service and norm_text_fn(service.department) in department_names:
                    inferred = department_names[norm_text_fn(service.department)]

            if not inferred and service_name:
                service = find_service_fn(session, service_name)
                if service and norm_text_fn(service.department) in department_names:
                    inferred = department_names[norm_text_fn(service.department)]

            if inferred:
                booking.department = inferred
                updated += 1
            elif current_department:
                booking.department = unknown_name
                updated += 1

        if updated:
            session.commit()
    except Exception as exc:
        session.rollback()
        print(f"Backfill warning (booking.department): {exc}")
    finally:
        session.close()


def normalize_money_precision(money_float_fn):
    session = SessionLocal()
    try:
        updated = 0

        for service in session.query(Service).all():
            old_price = float(service.price or 0)
            new_price = money_float_fn(old_price)
            if old_price != new_price:
                service.price = new_price
                updated += 1

        for booking in session.query(Booking).all():
            old_price = float(booking.price or 0)
            old_paid = float(booking.paid or 0)
            old_remaining = float(booking.remaining or 0)
            new_price = money_float_fn(old_price)
            new_paid = money_float_fn(old_paid)
            new_remaining = money_float_fn(old_remaining)
            if old_price != new_price or old_paid != new_paid or old_remaining != new_remaining:
                booking.price = new_price
                booking.paid = new_paid
                booking.remaining = new_remaining
                updated += 1

        for payment in session.query(Payment).all():
            old_amount = float(payment.amount or 0)
            old_remaining_after = float(payment.remaining_after or 0)
            new_amount = money_float_fn(old_amount)
            new_remaining_after = money_float_fn(old_remaining_after)
            if old_amount != new_amount or old_remaining_after != new_remaining_after:
                payment.amount = new_amount
                payment.remaining_after = new_remaining_after
                updated += 1

        if updated:
            session.commit()
    except Exception as exc:
        session.rollback()
        print(f"Money precision normalization warning: {exc}")
    finally:
        session.close()
