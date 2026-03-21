from __future__ import annotations

import os
import sys
import time
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import logic
from logic import SessionLocal, Booking, Customer, Service, Dress, Payment, Department


def _to_float(val):
    if val is None or str(val).strip() == "":
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except Exception:
        return None


def _norm_text(val):
    if val is None:
        return ""
    return str(val).replace("\u00A0", " ").strip()


def _check_duplicates(df, col):
    if col not in df.columns:
        return []
    series = df[col].astype(str).str.strip()
    dup = series[series.duplicated()]
    return sorted(set(dup.tolist()))


def _check_missing_refs():
    b_df = logic.load_data("bookings.csv", logic.B_COLS)
    c_df = logic.load_data("customers.csv", logic.C_COLS)
    s_df = logic.load_data("services.csv", logic.S_COLS)
    d_df = logic.load_data("dresses.csv", logic.D_COLS)
    p_df = logic.load_data("payments.csv", logic.P_COLS)
    dep_df = logic.check_departments() if hasattr(logic, "check_departments") else None

    missing = {}

    # Fallback-safe column selection by index to avoid encoding/rendering mismatches.
    b_customer_col = logic.B_COLS[2]
    c_customer_col = logic.C_COLS[2]
    b_service_col = logic.B_COLS[4]
    s_service_col = logic.S_COLS[2]
    b_dress_col = logic.B_COLS[5]
    d_dress_col = logic.D_COLS[0]
    p_booking_col = logic.P_COLS[2]
    b_booking_col = logic.B_COLS[0]
    b_dept_col = logic.B_COLS[3]

    # FK-style integrity checks using DB entities (with legacy fallback by name).
    session = SessionLocal()
    try:
        customers_by_id = {_norm_text(c.customer_id) for c in session.query(Customer).all()}
        services_by_id = {_norm_text(s.service_id) for s in session.query(Service).all()}
        customers_by_name = {_norm_text(c.name) for c in session.query(Customer).all()}
        services_by_name = {_norm_text(s.name) for s in session.query(Service).all()}

        missing_customer_ids = []
        missing_service_ids = []

        for b in session.query(Booking).all():
            b_customer_id = _norm_text(getattr(b, "customer_id", ""))
            b_customer_name = _norm_text(getattr(b, "customer_name", ""))
            if b_customer_id:
                if b_customer_id not in customers_by_id:
                    missing_customer_ids.append(b_customer_id)
            elif b_customer_name and b_customer_name != "-" and b_customer_name not in customers_by_name:
                missing_customer_ids.append(f"name:{b_customer_name}")

            b_service_id = _norm_text(getattr(b, "service_id", ""))
            b_service_name = _norm_text(getattr(b, "service", ""))
            if b_service_id:
                if b_service_id not in services_by_id:
                    missing_service_ids.append(b_service_id)
            elif b_service_name and b_service_name != "-" and b_service_name not in services_by_name:
                missing_service_ids.append(f"name:{b_service_name}")

        missing["bookings_missing_customer_ids"] = sorted(set(missing_customer_ids))
        missing["bookings_missing_service_ids"] = sorted(set(missing_service_ids))
    finally:
        session.close()

    # Keep legacy text checks visible during migration period.
    missing_customers = sorted(
        set(b_df[b_customer_col].astype(str).str.strip())
        - set(c_df[c_customer_col].astype(str).str.strip())
    )
    missing_customers = [m for m in missing_customers if m and m != "-"]
    missing["bookings_missing_customers"] = missing_customers

    missing_services = sorted(
        set(b_df[b_service_col].astype(str).str.strip())
        - set(s_df[s_service_col].astype(str).str.strip())
    )
    missing_services = [m for m in missing_services if m and m != "-"]
    missing["bookings_missing_services"] = missing_services

    booking_dress_codes = [
        logic._norm_code(x) for x in b_df[b_dress_col].tolist()
        if str(x).strip() not in ("", "-", "nan", "NaN")
    ]
    dress_codes = {logic._norm_code(x) for x in d_df[d_dress_col].tolist()}
    missing_dresses = sorted({c for c in booking_dress_codes if c and c not in dress_codes})
    missing["bookings_missing_dresses"] = missing_dresses

    missing_bookings = sorted(
        set(p_df[p_booking_col].astype(str).str.strip())
        - set(b_df[b_booking_col].astype(str).str.strip())
    )
    missing_bookings = [m for m in missing_bookings if m and m != "-"]
    missing["payments_missing_bookings"] = missing_bookings

    if dep_df is not None and not dep_df.empty:
        dep_col = "department_name" if "department_name" in dep_df.columns else dep_df.columns[0]
        missing_depts = sorted(
            set(b_df[b_dept_col].astype(str).str.strip())
            - set(dep_df[dep_col].astype(str).str.strip())
        )
        missing_depts = [m for m in missing_depts if m and m != "-"]
    else:
        missing_depts = []
    missing["bookings_missing_departments"] = missing_depts

    return missing
def _check_numeric_ranges():
    b_df = logic.load_data("bookings.csv", logic.B_COLS)
    p_df = logic.load_data("payments.csv", logic.P_COLS)
    b_booking_col = logic.B_COLS[0]
    b_price_col = logic.B_COLS[7]
    b_paid_col = logic.B_COLS[8]
    b_remaining_col = logic.B_COLS[9]
    p_id_col = logic.P_COLS[0]
    p_amount_col = logic.P_COLS[3]
    p_remaining_col = logic.P_COLS[6]

    numeric_issues = {
        "booking_price_invalid": [],
        "booking_paid_invalid": [],
        "booking_remaining_invalid": [],
        "payment_amount_invalid": [],
        "payment_remaining_invalid": [],
        "booking_mismatch_remaining": [],
    }

    for _, row in b_df.iterrows():
        price = _to_float(row.get(b_price_col))
        paid = _to_float(row.get(b_paid_col))
        remaining = _to_float(row.get(b_remaining_col))
        booking_id = row.get(b_booking_col, "")

        if price is None:
            numeric_issues["booking_price_invalid"].append(booking_id)
        elif price < 0:
            numeric_issues["booking_price_invalid"].append(booking_id)

        if paid is None:
            numeric_issues["booking_paid_invalid"].append(booking_id)
        elif paid < 0:
            numeric_issues["booking_paid_invalid"].append(booking_id)

        if remaining is None:
            numeric_issues["booking_remaining_invalid"].append(booking_id)

        if price is not None and paid is not None and remaining is not None:
            if abs((price - paid) - remaining) > 0.01:
                numeric_issues["booking_mismatch_remaining"].append(booking_id)

    for _, row in p_df.iterrows():
        payment_id = row.get(p_id_col, "")
        amount = _to_float(row.get(p_amount_col))
        rem = _to_float(row.get(p_remaining_col))
        if amount is None or amount < 0:
            numeric_issues["payment_amount_invalid"].append(payment_id)
        if rem is None:
            numeric_issues["payment_remaining_invalid"].append(payment_id)

    return numeric_issues


def _check_dates():
    date_issues = {}
    b_df = logic.load_data("bookings.csv", logic.B_COLS)
    c_df = logic.load_data("customers.csv", logic.C_COLS)
    p_df = logic.load_data("payments.csv", logic.P_COLS)
    d_df = logic.load_data("dresses.csv", logic.D_COLS)

    def find_invalid_dates(series):
        s = pd.to_datetime(series, errors="coerce")
        return series[s.isna() & series.astype(str).str.strip().ne("")].unique().tolist()

    date_issues["bookings_booking_date"] = find_invalid_dates(b_df[logic.B_COLS[1]])
    date_issues["bookings_event_date"] = find_invalid_dates(b_df[logic.B_COLS[6]])
    date_issues["customers_reg_date"] = find_invalid_dates(c_df[logic.C_COLS[1]])
    date_issues["payments_date"] = find_invalid_dates(p_df[logic.P_COLS[1]])
    date_issues["dresses_buy_date"] = find_invalid_dates(d_df[logic.D_COLS[2]])

    return date_issues


def _performance_check():
    results = {}
    for name, file_name, cols in [
        ("customers", "customers.csv", logic.C_COLS),
        ("services", "services.csv", logic.S_COLS),
        ("dresses", "dresses.csv", logic.D_COLS),
        ("bookings", "bookings.csv", logic.B_COLS),
        ("payments", "payments.csv", logic.P_COLS),
    ]:
        t0 = time.perf_counter()
        df = logic.load_data(file_name, cols)
        t1 = time.perf_counter()
        results[name] = {"rows": len(df), "seconds": round(t1 - t0, 4)}
    return results


def _roles_check():
    try:
        users = logic.check_users()
        roles = sorted(set(users["role"].astype(str).str.strip()))
        return {"total_users": len(users), "roles": roles}
    except Exception:
        return {"total_users": 0, "roles": []}


def _concurrency_test():
    session1 = SessionLocal()
    session2 = SessionLocal()
    session3 = SessionLocal()
    result = {"ran": False, "final_notes": None, "ok": False, "error": None}
    created_customer_id = None
    created_service_id = None
    booking_id = None
    try:
        cust = session1.query(Customer).first()
        svc = session1.query(Service).first()
        if not cust:
            ts = int(time.time() * 1000)
            created_customer_id = f"TST-C-{ts}"
            cust = Customer(
                customer_id=created_customer_id,
                reg_date=str(date.today()),
                name=f"Test Customer {ts}",
                groom_name="Test Groom",
                address="Test Address",
                phone1=f"999{str(ts)[-7:]}",
                phone2="",
                notes="health-check-temp",
            )
            session1.add(cust)
            session1.commit()

        if not svc:
            ts = int(time.time() * 1000)
            created_service_id = f"TST-S-{ts}"
            svc = Service(
                service_id=created_service_id,
                department=logic.DEPT_MAKEUP,
                name=f"Test Service {ts}",
                price=0.0,
            )
            session1.add(svc)
            session1.commit()

        dress_code = ""
        if svc.department == logic.DEPT_DRESSES:
            dress = session1.query(Dress).first()
            if dress:
                dress_code = dress.dress_code

        booking_id = f"TST-{int(time.time() * 1000)}"
        booking = Booking(
            booking_id=booking_id,
            booking_date=str(date.today()),
            customer_name=cust.name,
            customer_id=cust.customer_id,
            department=svc.department,
            service=svc.name,
            dress_code=dress_code,
            event_date=str(date.today()),
            price=100.0,
            paid=0.0,
            remaining=100.0,
            notes="concurrency-test",
        )
        session1.add(booking)
        session1.commit()

        b1 = session1.query(Booking).filter_by(booking_id=booking_id).first()
        b2 = session2.query(Booking).filter_by(booking_id=booking_id).first()
        if not b1 or not b2:
            result["error"] = "Failed to load booking in both sessions."
            return result

        b1.notes = "concurrency-1"
        session1.commit()
        b2.notes = "concurrency-2"
        session2.commit()

        final = session3.query(Booking).filter_by(booking_id=booking_id).first()
        result["ran"] = True
        result["final_notes"] = final.notes if final else None
        result["ok"] = final is not None
    except Exception as e:
        result["error"] = str(e)
    finally:
        try:
            if booking_id:
                booking = session3.query(Booking).filter_by(booking_id=booking_id).first()
                if booking:
                    session3.delete(booking)
            if created_service_id:
                svc_row = session3.query(Service).filter_by(service_id=created_service_id).first()
                if svc_row:
                    session3.delete(svc_row)
            if created_customer_id:
                cust_row = session3.query(Customer).filter_by(customer_id=created_customer_id).first()
                if cust_row:
                    session3.delete(cust_row)
            session3.commit()
        except Exception:
            session3.rollback()
        session1.close()
        session2.close()
        session3.close()
    return result


def _to_decimal(val):
    if val is None:
        return None
    raw = str(val).strip()
    if raw == "":
        return None
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError, TypeError):
        return None


def _check_money_precision():
    issues = {
        "service_price_scale_invalid": [],
        "booking_price_scale_invalid": [],
        "booking_paid_scale_invalid": [],
        "booking_remaining_scale_invalid": [],
        "payment_amount_scale_invalid": [],
        "payment_remaining_after_scale_invalid": [],
    }

    def _is_2dp(value):
        dec = _to_decimal(value)
        if dec is None:
            return False
        return dec == dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    session = SessionLocal()
    try:
        for s in session.query(Service).all():
            if not _is_2dp(s.price):
                issues["service_price_scale_invalid"].append(s.service_id)

        for b in session.query(Booking).all():
            if not _is_2dp(b.price):
                issues["booking_price_scale_invalid"].append(b.booking_id)
            if not _is_2dp(b.paid):
                issues["booking_paid_scale_invalid"].append(b.booking_id)
            if not _is_2dp(b.remaining):
                issues["booking_remaining_scale_invalid"].append(b.booking_id)

        for p in session.query(Payment).all():
            if not _is_2dp(p.amount):
                issues["payment_amount_scale_invalid"].append(p.payment_id)
            if not _is_2dp(p.remaining_after):
                issues["payment_remaining_after_scale_invalid"].append(p.payment_id)
    finally:
        session.close()

    return issues


def _check_money_schema_migration_idempotence():
    result = {"ran": False, "ok": False, "error": None, "types_before": {}, "types_after": {}, "counts_before": {}, "counts_after": {}}
    if logic.engine.url.get_backend_name() != "sqlite":
        result["error"] = "Skipped (non-sqlite backend)."
        return result

    session = SessionLocal()
    try:
        tables = ["services", "bookings", "payments"]
        money_cols = {
            "services": ["price"],
            "bookings": ["price", "paid", "remaining"],
            "payments": ["amount", "remaining_after"],
        }

        def _snapshot():
            types = {}
            counts = {}
            for t in tables:
                counts[t] = int(session.execute(logic.text(f"SELECT COUNT(*) FROM {t}")).scalar() or 0)
                rows = session.execute(logic.text(f"PRAGMA table_info({t})")).fetchall()
                cols = {str(r[1]).strip(): str(r[2]).strip().upper() for r in rows}
                types[t] = {c: cols.get(c, "") for c in money_cols[t]}
            return types, counts

        before_types, before_counts = _snapshot()
        # Should be safe to call multiple times; it should no-op when schema is already migrated.
        logic._migrate_sqlite_money_columns_to_numeric()
        logic._migrate_sqlite_money_columns_to_numeric()
        after_types, after_counts = _snapshot()

        result["ran"] = True
        result["types_before"] = before_types
        result["types_after"] = after_types
        result["counts_before"] = before_counts
        result["counts_after"] = after_counts
        result["ok"] = before_types == after_types and before_counts == after_counts
        return result
    except Exception as e:
        result["error"] = str(e)
        return result
    finally:
        session.close()


def _layout_render_smoke():
    result = {"ok": False, "error": None}
    try:
        import app_dash

        app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        result["ok"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def _collect_component_ids(node, out_ids):
    if node is None:
        return
    if isinstance(node, (list, tuple)):
        for item in node:
            _collect_component_ids(item, out_ids)
        return

    comp_id = getattr(node, "id", None)
    if isinstance(comp_id, str) and comp_id:
        out_ids.add(comp_id)

    children = getattr(node, "children", None)
    if children is not None:
        _collect_component_ids(children, out_ids)


def _main_nav_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "nav-finance",
            "nav-bookings",
            "nav-customers",
            "nav-services",
            "nav-dresses",
            "nav-payments",
            "nav-settings",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _critical_action_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "btn-add-service-modal",
            "btn-save-service",
            "btn-add-customer-modal",
            "btn-save-customer",
            "btn-add-booking-modal",
            "btn-save-booking",
            "btn-add-payment-modal",
            "btn-save-payment",
            "btn-delete-booking",
            "btn-delete-service",
            "btn-delete-customer",
            "btn-delete-payment",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _table_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "customers-table-container",
            "services-table-container",
            "dresses-table-container",
            "bookings-table-container",
            "payments-table-container",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _booking_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-booking",
            "b-dept",
            "b-customer",
            "b-service",
            "b-dress",
            "b-date",
            "b-event-date",
            "b-price",
            "b-paid",
            "b-notes",
            "b-alert",
            "btn-save-booking",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _payments_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-payment",
            "p-search",
            "p-date",
            "p-amount",
            "p-booking",
            "p-booking-details",
            "p-notes",
            "p-alert",
            "btn-add-payment-modal",
            "btn-save-payment",
            "btn-edit-payment",
            "btn-delete-payment",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _settings_departments_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "btn-add-dept-modal",
            "dept-search",
            "btn-edit-dept",
            "btn-delete-dept",
            "dept-edit-id",
            "dept-alert",
            "dept-table-container",
            "modal-dept",
            "dept-modal-title",
            "dept-name",
            "btn-save-dept",
            "modal-delete-dept",
            "btn-cancel-delete-dept",
            "btn-confirm-delete-dept",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _delete_confirm_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-delete-customer",
            "btn-cancel-delete",
            "btn-confirm-delete",
            "modal-delete-service",
            "btn-cancel-delete-s",
            "btn-confirm-delete-s",
            "modal-delete-dress",
            "btn-cancel-delete-d",
            "btn-confirm-delete-d",
            "modal-delete-booking",
            "btn-cancel-delete-b",
            "btn-confirm-delete-b",
            "modal-delete-payment",
            "btn-cancel-delete-p",
            "btn-confirm-delete-p",
            "modal-delete-dept",
            "btn-cancel-delete-dept",
            "btn-confirm-delete-dept",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _customers_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-customer",
            "c-name",
            "c-groom",
            "c-phone1",
            "c-phone2",
            "c-addr",
            "c-reg-date",
            "c-notes",
            "c-add-alert",
            "btn-save-customer",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _services_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-service",
            "s-name",
            "s-dept",
            "s-price",
            "s-alert",
            "btn-save-service",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _dresses_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-dress",
            "d-code",
            "d-type",
            "d-date",
            "d-status",
            "d-desc",
            "d-upload-image",
            "d-upload-output",
            "d-alert",
            "btn-save-dress",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _quick_add_and_details_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "btn-quick-add-customer",
            "modal-details-viewer",
            "details-viewer-title",
            "details-viewer-body",
            "btn-close-details",
            "p-booking-details",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result


def _auth_error_text_localization_smoke():
    result = {"ok": False, "error": None}
    try:
        path = os.path.join(ROOT, "app", "callbacks", "auth.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        has_ar = "خطأ أثناء تحميل الصفحة" in content
        has_en = "Error Loading Page" in content
        result["ok"] = has_ar and (not has_en)
        if not result["ok"]:
            result["error"] = (
                f"localized_title_present={has_ar}, english_title_present={has_en}"
            )
    except Exception as e:
        result["error"] = str(e)
    return result


def _export_callback_registered_smoke():
    result = {"ok": False, "matches": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        matches = [k for k in cb_map.keys() if "exportDataAsCsv" in str(k)]
        result["matches"] = matches
        result["ok"] = len(matches) > 0
        if not result["ok"]:
            result["error"] = "No callback output found for exportDataAsCsv"
    except Exception as e:
        result["error"] = str(e)
    return result


def _details_callback_registered_smoke():
    result = {"ok": False, "matches": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        matches = [k for k in cb_map.keys() if "modal-details-viewer.is_open" in str(k)]
        result["matches"] = matches
        result["ok"] = len(matches) > 0
        if not result["ok"]:
            result["error"] = "No callback output found for modal-details-viewer.is_open"
    except Exception as e:
        result["error"] = str(e)
    return result


def _bookings_callback_registered_smoke():
    result = {"ok": False, "matches": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        matches = [k for k in cb_map.keys() if "modal-booking.is_open" in str(k)]
        result["matches"] = matches
        result["ok"] = len(matches) > 0
        if not result["ok"]:
            result["error"] = "No callback output found for modal-booking.is_open"
    except Exception as e:
        result["error"] = str(e)
    return result


def _reactive_dropdown_wiring_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        keys = list(cb_map.keys())
        required_outputs = [
            "s-dept.options",
            "c-search.options",
            "c-search.value",
            "s-search.options",
            "s-search.value",
            "d-search.options",
            "d-search.value",
            "b-search.options",
            "b-search.value",
            "p-search.options",
            "p-search.value",
            "dept-search.options",
            "dept-search.value",
            "b-dept.options",
            "b-customer.options",
            "b-customer.value",
            "b-service.options",
            "b-service.value",
            "b-dress.options",
            "dress-section.style",
            "p-booking.options",
            "p-booking.value",
        ]
        missing = [needle for needle in required_outputs if not any(needle in str(k) for k in keys)]
        result["missing"] = missing
        result["ok"] = len(missing) == 0
    except Exception as e:
        result["error"] = str(e)
    return result


def _quick_add_customer_wiring_smoke():
    result = {"ok": False, "matches": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        matches = []
        for output_key, meta in cb_map.items():
            out_str = str(output_key)
            if "b-customer.options" not in out_str and "b-customer.value" not in out_str:
                continue
            inputs = meta.get("inputs", []) or []
            has_quick_add_input = any(
                str(i.get("id")) == "last-added-customer" and str(i.get("property")) == "data"
                for i in inputs
            )
            if has_quick_add_input:
                matches.append(out_str)

        result["matches"] = matches
        result["ok"] = len(matches) > 0
        if not result["ok"]:
            result["error"] = "No b-customer callback wired to last-added-customer.data"
    except Exception as e:
        result["error"] = str(e)
    return result


def main():
    # Ensure DB schema is up-to-date before ORM-based checks.
    logic.init_folders()
    print("=== Health Check Report ===")
    print("Performance:", _performance_check())
    print("Roles:", _roles_check())
    print("Duplicates:")
    c_df = logic.load_data("customers.csv", logic.C_COLS)
    s_df = logic.load_data("services.csv", logic.S_COLS)
    d_df = logic.load_data("dresses.csv", logic.D_COLS)
    b_df = logic.load_data("bookings.csv", logic.B_COLS)
    p_df = logic.load_data("payments.csv", logic.P_COLS)
    print("  customers:", _check_duplicates(c_df, logic.C_COLS[0]))
    print("  services:", _check_duplicates(s_df, logic.S_COLS[0]))
    print("  dresses:", _check_duplicates(d_df, logic.D_COLS[0]))
    print("  bookings:", _check_duplicates(b_df, logic.B_COLS[0]))
    print("  payments:", _check_duplicates(p_df, logic.P_COLS[0]))

    print("Missing references:", _check_missing_refs())
    print("Numeric issues:", _check_numeric_ranges())
    print("Money precision:", _check_money_precision())
    print("Money schema idempotence:", _check_money_schema_migration_idempotence())
    print("Layout render smoke:", _layout_render_smoke())
    print("Main nav ids smoke:", _main_nav_ids_smoke())
    print("Critical action ids smoke:", _critical_action_ids_smoke())
    print("Table ids smoke:", _table_ids_smoke())
    print("Booking form ids smoke:", _booking_form_ids_smoke())
    print("Payments form ids smoke:", _payments_form_ids_smoke())
    print("Settings departments ids smoke:", _settings_departments_ids_smoke())
    print("Delete confirm ids smoke:", _delete_confirm_ids_smoke())
    print("Customers form ids smoke:", _customers_form_ids_smoke())
    print("Services form ids smoke:", _services_form_ids_smoke())
    print("Dresses form ids smoke:", _dresses_form_ids_smoke())
    print("Quick-add/details ids smoke:", _quick_add_and_details_ids_smoke())
    print("Auth error text localization smoke:", _auth_error_text_localization_smoke())
    print("Export callback registered smoke:", _export_callback_registered_smoke())
    print("Details callback registered smoke:", _details_callback_registered_smoke())
    print("Bookings callback registered smoke:", _bookings_callback_registered_smoke())
    print("Reactive dropdown wiring smoke:", _reactive_dropdown_wiring_smoke())
    print("Quick-add customer wiring smoke:", _quick_add_customer_wiring_smoke())
    print("Date issues:", _check_dates())
    print("Concurrency test:", _concurrency_test())


if __name__ == "__main__":
    main()



