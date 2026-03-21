import dash_bootstrap_components as dbc
import logic


def build_payments_table_content(load_data, create_dt, p_cols, payment_booking_action_label):
    df = load_data("payments.csv", p_cols)
    if df.empty:
        return dbc.Alert("لا توجد دفعات.", color="info")

    # Normalize payment date for display.
    if len(p_cols) >= 2 and p_cols[1] in df.columns:
        df[p_cols[1]] = df[p_cols[1]].apply(logic.format_date_ddmmyyyy)

    return create_dt(
        df.iloc[::-1],
        "payments-table",
        "payments.csv",
        action_buttons={
            "field": "__action__",
            "col_id": "view-booking-action",
            "label": payment_booking_action_label,
            "mobile_type": "view-booking",
            "mobile_color": "info",
            "header": "",
            "minWidth": 140,
            "maxWidth": 170,
        },
        row_id_field=p_cols[0] if p_cols else None,
        mobile_card_fields=[p_cols[2], p_cols[1], p_cols[3], p_cols[6]] if len(p_cols) > 6 else p_cols[1:4],
        mobile_title_field=p_cols[4] if len(p_cols) > 4 else (p_cols[0] if p_cols else None),
        mobile_select_target="p-search",
    )
