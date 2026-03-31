import pandas as pd
from dash import Input, Output, State, ctx, no_update

from app.callbacks.bookings_form_helpers import (
    build_booking_customer_options,
    build_booking_dress_options,
    build_booking_service_options_for_dept,
)


def register_bookings_form_option_callbacks(
    app,
    load_data,
    c_cols,
    s_cols,
    d_cols,
    normalize_code,
    is_dresses_dept,
):
    def _rows_to_df(rows):
        if not isinstance(rows, list) or not rows:
            return pd.DataFrame()
        return pd.DataFrame.from_records(rows)

    @app.callback(
        [Output("b-customer", "options", allow_duplicate=True), Output("b-customer", "value", allow_duplicate=True)],
        Input("last-added-customer", "data"),
        [State("modal-booking", "is_open"), State("customers_data", "data")],
        prevent_initial_call=True,
    )
    def refresh_booking_customers_after_quick_add(last_added_customer, is_booking_open, customers_data):
        if not is_booking_open or not last_added_customer:
            return no_update, no_update
        rows = customers_data if isinstance(customers_data, list) and customers_data else load_data("customers.csv", c_cols).to_dict("records")
        options = build_booking_customer_options(_rows_to_df(rows), c_cols)
        if last_added_customer not in {opt["value"] for opt in options}:
            rows = load_data("customers.csv", c_cols).to_dict("records")
            options = build_booking_customer_options(_rows_to_df(rows), c_cols)
        if not options:
            return no_update, no_update
        selected = last_added_customer if last_added_customer in {opt["value"] for opt in options} else no_update
        return options, selected

    @app.callback(
        [Output("b-dept", "options"), Output("b-dept", "value", allow_duplicate=True)],
        [Input("departments_search_options", "data"), Input("modal-booking", "is_open")],
        State("b-dept", "value"),
        prevent_initial_call=True,
    )
    def refresh_booking_department_options(department_options, is_open, current_dept):
        if not is_open:
            return no_update, no_update
        options = department_options if isinstance(department_options, list) else []
        valid_values = {opt["value"] for opt in options}
        return options, current_dept if current_dept in valid_values else None

    @app.callback(
        [Output("b-customer", "options", allow_duplicate=True), Output("b-customer", "value", allow_duplicate=True)],
        [
            Input("customers_data", "data"),
            Input("last-added-customer", "data"),
            Input("modal-booking", "is_open"),
        ],
        State("b-customer", "value"),
        prevent_initial_call=True,
    )
    def refresh_booking_customer_options(customers_data, last_added_customer, is_open, current_customer):
        if not is_open:
            return no_update, no_update
        if ctx.triggered_id == "modal-booking":
            rows = load_data("customers.csv", c_cols).to_dict("records")
        else:
            rows = customers_data if isinstance(customers_data, list) and customers_data else load_data("customers.csv", c_cols).to_dict("records")
        options = build_booking_customer_options(_rows_to_df(rows), c_cols)
        valid_values = {opt["value"] for opt in options}
        if last_added_customer and last_added_customer not in valid_values:
            rows = load_data("customers.csv", c_cols).to_dict("records")
            options = build_booking_customer_options(_rows_to_df(rows), c_cols)
            valid_values = {opt["value"] for opt in options}
        if current_customer in valid_values:
            next_value = current_customer
        elif last_added_customer in valid_values:
            next_value = last_added_customer
        else:
            next_value = None
        return options, next_value

    @app.callback(
        [Output("b-dress", "options", allow_duplicate=True), Output("b-dress", "value", allow_duplicate=True)],
        [Input("dresses_data", "data"), Input("modal-booking", "is_open")],
        State("b-dress", "value"),
        prevent_initial_call=True,
    )
    def refresh_booking_dress_options(dresses_data, is_open, current_dress):
        if not is_open:
            return no_update, no_update
        rows = dresses_data if isinstance(dresses_data, list) and dresses_data else load_data("dresses.csv", d_cols).to_dict("records")
        options = build_booking_dress_options(_rows_to_df(rows), d_cols)
        valid_norm = {normalize_code(opt["value"]) for opt in options}
        current_norm = normalize_code(current_dress)
        next_value = current_dress if current_norm and current_norm in valid_norm else None
        return options, next_value

    @app.callback(
        [
            Output("b-service", "options", allow_duplicate=True),
            Output("b-service", "value", allow_duplicate=True),
            Output("dress-section", "style", allow_duplicate=True),
        ],
        [Input("services_data", "data"), Input("b-dept", "value"), Input("modal-booking", "is_open")],
        State("b-service", "value"),
        prevent_initial_call=True,
    )
    def refresh_booking_service_options(services_data, dept, is_open, current_service):
        if not is_open:
            return no_update, no_update, no_update
        if not dept:
            return [], None, {"display": "none"}
        if ctx.triggered_id in {"b-dept", "modal-booking"}:
            rows = load_data("services.csv", s_cols).to_dict("records")
        else:
            rows = services_data if isinstance(services_data, list) and services_data else load_data("services.csv", s_cols).to_dict("records")
        options = build_booking_service_options_for_dept(_rows_to_df(rows), s_cols, dept)
        valid_values = {opt["value"] for opt in options}
        next_value = current_service if current_service in valid_values else None
        return options, next_value, {"display": "block"} if is_dresses_dept(dept) else {"display": "none"}
