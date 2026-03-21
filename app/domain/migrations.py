import os
import sqlite3

from sqlalchemy import text

from models import Booking, Department, Payment, Service, SessionLocal


def ensure_booking_service_id_column(engine):
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("PRAGMA table_info(bookings)")).fetchall()
            cols = {str(r[1]).strip().lower() for r in rows}
            if "service_id" not in cols:
                conn.execute(text("ALTER TABLE bookings ADD COLUMN service_id VARCHAR"))
                conn.commit()
        return True
    except Exception as e:
        print(f"Schema migration warning (service_id): {e}")
        return False


def ensure_booking_status_column(engine, default_status):
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("PRAGMA table_info(bookings)")).fetchall()
            cols = {str(r[1]).strip().lower() for r in rows}
            if "status" not in cols:
                conn.execute(text("ALTER TABLE bookings ADD COLUMN status VARCHAR"))
            conn.execute(
                text(
                    "UPDATE bookings SET status = :default_status "
                    "WHERE status IS NULL OR TRIM(status) = ''"
                ),
                {"default_status": default_status},
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Schema migration warning (booking_status): {e}")
        return False


def migrate_sqlite_money_columns_to_numeric(engine):
    try:
        if engine.url.get_backend_name() != "sqlite":
            return
        db_path = engine.url.database
        if not db_path or not os.path.exists(db_path):
            return

        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()

            def col_type(table, col):
                rows = cur.execute(f"PRAGMA table_info({table})").fetchall()
                for r in rows:
                    if str(r[1]).strip().lower() == col.lower():
                        return str(r[2] or "").strip().upper()
                return ""

            money_cols = {
                "services": ("price",),
                "bookings": ("price", "paid", "remaining"),
                "payments": ("amount", "remaining_after"),
            }
            need = False
            for t, cols in money_cols.items():
                for c in cols:
                    typ = col_type(t, c)
                    if typ and typ.startswith("NUMERIC"):
                        continue
                    need = True
                    break
                if need:
                    break

            if not need:
                return

            conn.executescript(
                """
                PRAGMA foreign_keys=OFF;

                CREATE TABLE services_new (
                    service_id VARCHAR PRIMARY KEY,
                    department VARCHAR,
                    name VARCHAR,
                    price NUMERIC(12,2)
                );
                INSERT INTO services_new(service_id, department, name, price)
                SELECT service_id, department, name, ROUND(CAST(COALESCE(price, 0) AS REAL), 2)
                FROM services;
                DROP TABLE services;
                ALTER TABLE services_new RENAME TO services;
                CREATE INDEX IF NOT EXISTS ix_services_department ON services(department);

                CREATE TABLE bookings_new (
                    booking_id VARCHAR PRIMARY KEY,
                    booking_date VARCHAR,
                    customer_name VARCHAR,
                    customer_id VARCHAR REFERENCES customers(customer_id),
                    department VARCHAR,
                    service VARCHAR,
                    dress_code VARCHAR,
                    event_date VARCHAR,
                    price NUMERIC(12,2),
                    paid NUMERIC(12,2),
                    remaining NUMERIC(12,2),
                    notes VARCHAR,
                    service_id VARCHAR
                );
                INSERT INTO bookings_new(
                    booking_id, booking_date, customer_name, customer_id, department, service,
                    dress_code, event_date, price, paid, remaining, notes, service_id
                )
                SELECT
                    booking_id, booking_date, customer_name, customer_id, department, service,
                    dress_code, event_date,
                    ROUND(CAST(COALESCE(price, 0) AS REAL), 2),
                    ROUND(CAST(COALESCE(paid, 0) AS REAL), 2),
                    ROUND(CAST(COALESCE(remaining, 0) AS REAL), 2),
                    notes, service_id
                FROM bookings;
                DROP TABLE bookings;
                ALTER TABLE bookings_new RENAME TO bookings;

                CREATE TABLE payments_new (
                    payment_id VARCHAR PRIMARY KEY,
                    payment_date VARCHAR,
                    booking_id VARCHAR REFERENCES bookings(booking_id),
                    amount NUMERIC(12,2),
                    customer_name VARCHAR,
                    groom_name VARCHAR,
                    remaining_after NUMERIC(12,2),
                    notes VARCHAR
                );
                INSERT INTO payments_new(
                    payment_id, payment_date, booking_id, amount, customer_name, groom_name, remaining_after, notes
                )
                SELECT
                    payment_id, payment_date, booking_id,
                    ROUND(CAST(COALESCE(amount, 0) AS REAL), 2),
                    customer_name, groom_name,
                    ROUND(CAST(COALESCE(remaining_after, 0) AS REAL), 2),
                    notes
                FROM payments;
                DROP TABLE payments;
                ALTER TABLE payments_new RENAME TO payments;

                PRAGMA foreign_keys=ON;
                """
            )
            conn.commit()
    except Exception as e:
        print(f"Schema migration warning (money_numeric): {e}")


def backfill_booking_service_ids(find_service_fn):
    session = SessionLocal()
    try:
        updated = 0
        for b in session.query(Booking).all():
            if getattr(b, "service_id", None):
                continue
            service_obj = find_service_fn(session, b.service, dept=b.department)
            if service_obj:
                b.service_id = service_obj.service_id
                b.service = service_obj.name
                updated += 1
        if updated:
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Backfill warning (booking.service_id): {e}")
    finally:
        session.close()


def backfill_service_departments(norm_text_fn, ensure_unknown_department_fn):
    session = SessionLocal()
    try:
        departments = session.query(Department).all()
        dept_names = {norm_text_fn(d.department_name): d.department_name for d in departments}
        unknown_name = ensure_unknown_department_fn(session)
        dept_names[norm_text_fn(unknown_name)] = unknown_name
        updated = 0

        for svc in session.query(Service).all():
            current = norm_text_fn(getattr(svc, "department", ""))
            if current in dept_names:
                continue
            svc.department = unknown_name
            updated += 1

        if updated:
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Backfill warning (service.department): {e}")
    finally:
        session.close()


def backfill_booking_departments(norm_text_fn, ensure_unknown_department_fn, find_service_fn):
    session = SessionLocal()
    try:
        departments = session.query(Department).all()
        dept_names = {norm_text_fn(d.department_name): d.department_name for d in departments}
        unknown_name = ensure_unknown_department_fn(session)
        dept_names[norm_text_fn(unknown_name)] = unknown_name
        updated = 0

        for b in session.query(Booking).all():
            current_dept = norm_text_fn(getattr(b, "department", ""))
            if current_dept in dept_names:
                continue

            inferred = None
            service_id = norm_text_fn(getattr(b, "service_id", ""))
            service_name = norm_text_fn(getattr(b, "service", ""))

            if service_id:
                svc = session.query(Service).filter_by(service_id=service_id).first()
                if svc and norm_text_fn(svc.department) in dept_names:
                    inferred = dept_names[norm_text_fn(svc.department)]

            if not inferred and service_name:
                svc = find_service_fn(session, service_name)
                if svc and norm_text_fn(svc.department) in dept_names:
                    inferred = dept_names[norm_text_fn(svc.department)]

            if inferred:
                b.department = inferred
                updated += 1
            elif current_dept:
                b.department = unknown_name
                updated += 1

        if updated:
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Backfill warning (booking.department): {e}")
    finally:
        session.close()


def normalize_money_precision(money_float_fn):
    session = SessionLocal()
    try:
        updated = 0

        for s in session.query(Service).all():
            old_price = float(s.price or 0)
            new_price = money_float_fn(old_price)
            if old_price != new_price:
                s.price = new_price
                updated += 1

        for b in session.query(Booking).all():
            old_price = float(b.price or 0)
            old_paid = float(b.paid or 0)
            old_remaining = float(b.remaining or 0)
            new_price = money_float_fn(old_price)
            new_paid = money_float_fn(old_paid)
            new_remaining = money_float_fn(old_remaining)
            if old_price != new_price or old_paid != new_paid or old_remaining != new_remaining:
                b.price = new_price
                b.paid = new_paid
                b.remaining = new_remaining
                updated += 1

        for p in session.query(Payment).all():
            old_amount = float(p.amount or 0)
            old_remaining_after = float(p.remaining_after or 0)
            new_amount = money_float_fn(old_amount)
            new_remaining_after = money_float_fn(old_remaining_after)
            if old_amount != new_amount or old_remaining_after != new_remaining_after:
                p.amount = new_amount
                p.remaining_after = new_remaining_after
                updated += 1

        if updated:
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Money precision normalization warning: {e}")
    finally:
        session.close()
