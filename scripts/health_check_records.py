from health_check_context import *

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
