from health_check_context import *

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
