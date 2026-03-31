import pandas as pd
import dash_bootstrap_components as dbc
from dash import html


def fmt_money(value):
    try:
        return f"{float(value):,.2f}"
    except Exception:
        return str(value or "0")


def records_to_dataframe(records):
    if not isinstance(records, list) or not records:
        return pd.DataFrame()
    return pd.DataFrame.from_records(records)


def build_booking_options(load_data, b_cols, booking_records=None):
    rows = booking_records if isinstance(booking_records, list) else None
    if rows is None:
        bookings_df = load_data("bookings.csv", b_cols)
        rows = bookings_df.to_dict("records") if not bookings_df.empty else []
    else:
        bookings_df = records_to_dataframe(rows)
    if not rows:
        return [], bookings_df

    booking_id_col = b_cols[0]
    customer_col = b_cols[2] if len(b_cols) > 2 else booking_id_col
    service_col = b_cols[4] if len(b_cols) > 4 else booking_id_col
    remaining_col = b_cols[9] if len(b_cols) > 9 else None
    options = []
    for row in rows:
        customer_name = str(row.get(customer_col, "")).strip()
        service_name = str(row.get(service_col, "")).strip()
        if remaining_col is not None:
            remaining_val = fmt_money(row.get(remaining_col, 0))
            label = f"{customer_name} ({service_name}) - المتبقي: {remaining_val}"
        else:
            label = f"{customer_name} ({service_name})"
        booking_id = row.get(booking_id_col)
        if booking_id is None:
            continue
        options.append({"label": label, "value": booking_id})
    return options, bookings_df


def build_booking_details(selected_booking_id, bookings_data, load_data, b_cols):
    if not selected_booking_id:
        return html.Div("اختر حجزًا لعرض المتبقي الحالي.")

    _, bookings_df = build_booking_options(load_data, b_cols, bookings_data)
    if bookings_df.empty:
        return dbc.Alert("لا توجد بيانات حجز متاحة.", color="warning")

    booking_id_col = b_cols[0]
    customer_col = b_cols[2] if len(b_cols) > 2 else booking_id_col
    service_col = b_cols[4] if len(b_cols) > 4 else booking_id_col
    price_col = b_cols[7] if len(b_cols) > 7 else None
    paid_col = b_cols[8] if len(b_cols) > 8 else None
    remaining_col = b_cols[9] if len(b_cols) > 9 else None
    row = bookings_df[bookings_df[booking_id_col] == selected_booking_id]
    if row.empty:
        return dbc.Alert("تعذر تحميل تفاصيل الحجز.", color="warning")

    record = row.iloc[0]
    details = [
        html.Div(f"كود الحجز: {record.get(booking_id_col, '-')}", className="fw-bold"),
        html.Div(f"العروسة: {record.get(customer_col, '-')}"),
        html.Div(f"الخدمة: {record.get(service_col, '-')}"),
    ]
    if price_col:
        details.append(html.Div(f"السعر المتفق: {fmt_money(record.get(price_col, 0))}"))
    if paid_col:
        details.append(html.Div(f"المدفوع: {fmt_money(record.get(paid_col, 0))}"))
    if remaining_col:
        details.append(html.Div(f"المتبقي الحالي: {fmt_money(record.get(remaining_col, 0))}", className="fw-bold"))
    return html.Div(details)
