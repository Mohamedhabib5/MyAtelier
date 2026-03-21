import dash_bootstrap_components as dbc
import logic


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _payment_progress_text(paid_value, price_value):
    price = max(_safe_float(price_value), 0.0)
    paid = max(_safe_float(paid_value), 0.0)
    pct = 0 if price <= 0 else int(round((min(paid, price) / price) * 100))

    # Textual bar keeps the change local to table data without custom renderers.
    filled = max(0, min(10, int(round(pct / 10))))
    bar = ("#" * filled) + ("-" * (10 - filled))
    if pct >= 100:
        icon = "[OK]"
    elif pct >= 50:
        icon = "[MID]"
    else:
        icon = "[LOW]"
    return f"{icon} {bar} {pct}%"


def _normalize_booking_status(value):
    text = logic._norm_text(value)
    allowed = {"\u0646\u0634\u0637", "\u0645\u0643\u062a\u0645\u0644", "\u0645\u0644\u063a\u064a"}
    return text if text in allowed else logic.BOOKING_STATUS_ACTIVE


def build_bookings_table_content(load_data, create_dt, b_cols, c_cols, d_cols, payments_action_label):
    df = load_data("bookings.csv", b_cols)
    if df.empty:
        return dbc.Alert("لا توجد حجوزات.", color="info")

    # Merge with customers (groom and phones)
    c_df = load_data("customers.csv", c_cols)
    if not c_df.empty and len(c_cols) >= 7 and len(b_cols) >= 3:
        customer_name_col = c_cols[2]
        customer_merge_cols = [c_cols[2], c_cols[3], c_cols[5], c_cols[6]]
        c_info_cols = [c for c in customer_merge_cols if c in c_df.columns]
        if c_info_cols and b_cols[2] in df.columns:
            c_info = c_df[c_info_cols]
            if customer_name_col in c_info.columns:
                if b_cols[2] == customer_name_col:
                    df = df.merge(c_info, on=b_cols[2], how="left")
                else:
                    df = df.merge(c_info, left_on=b_cols[2], right_on=customer_name_col, how="left")

    # Merge with dresses (description)
    d_df = load_data("dresses.csv", d_cols)
    if not d_df.empty and len(d_cols) >= 4 and len(b_cols) >= 6:
        dress_code_col = d_cols[0]
        dress_merge_cols = [d_cols[0], d_cols[3]]
        d_info_cols = [c for c in dress_merge_cols if c in d_df.columns]
        if d_info_cols and b_cols[5] in df.columns:
            d_info = d_df[d_info_cols]
            if dress_code_col in d_info.columns:
                if b_cols[5] == dress_code_col:
                    df = df.merge(d_info, on=b_cols[5], how="left")
                else:
                    df = df.merge(d_info, left_on=b_cols[5], right_on=dress_code_col, how="left")

    # Add payment progress indicator (paid/price) for quick scan.
    if len(b_cols) >= 9 and b_cols[7] in df.columns and b_cols[8] in df.columns:
        df["مؤشر السداد"] = df.apply(
            lambda row: _payment_progress_text(row[b_cols[8]], row[b_cols[7]]),
            axis=1,
        )

    # Normalize booking dates for display.
    if len(b_cols) >= 7:
        booking_date_col = b_cols[1]
        event_date_col = b_cols[6]
        if booking_date_col in df.columns:
            df[booking_date_col] = df[booking_date_col].apply(logic.format_date_ddmmyyyy)
        if event_date_col in df.columns:
            df[event_date_col] = df[event_date_col].apply(logic.format_date_ddmmyyyy)
    if len(b_cols) >= 12 and b_cols[11] in df.columns:
        df[b_cols[11]] = df[b_cols[11]].apply(_normalize_booking_status)

    return create_dt(
        df.iloc[::-1],
        "bookings-table",
        "bookings.csv",
        action_buttons={
            "field": "__action__",
            "col_id": "view-payments-action",
            "label": payments_action_label,
            "mobile_type": "view-payments",
            "mobile_color": "info",
            "header": "",
            "minWidth": 140,
            "maxWidth": 170,
        },
        row_id_field=b_cols[0] if b_cols else None,
        mobile_card_fields=[b_cols[4], b_cols[6], b_cols[9], b_cols[11]] if len(b_cols) > 11 else b_cols[1:5],
        mobile_title_field=b_cols[2] if len(b_cols) > 2 else (b_cols[0] if b_cols else None),
        mobile_select_target="b-search",
    )
