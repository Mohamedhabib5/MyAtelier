import dash_bootstrap_components as dbc


def build_customers_table_content(load_data, create_dt, c_cols, customer_bookings_action_label):
    df = load_data("customers.csv", c_cols)
    if df.empty:
        return dbc.Alert("لا يوجد عملاء.", color="info")

    row_id_field = c_cols[0] if c_cols and c_cols[0] in df.columns else None

    return create_dt(
        df,
        "customers-table",
        "customers.csv",
        action_buttons={
            "field": "__action__",
            "col_id": "view-customer-bookings-action",
            "label": customer_bookings_action_label,
            "mobile_type": "view-customer-bookings",
            "mobile_color": "info",
            "header": "",
            "minWidth": 150,
            "maxWidth": 190,
        },
        row_id_field=row_id_field,
        mobile_card_fields=[c_cols[3], c_cols[5], c_cols[4]] if len(c_cols) > 5 else c_cols[1:4],
        mobile_title_field=c_cols[2] if len(c_cols) > 2 else row_id_field,
        mobile_select_target="c-search",
    )
