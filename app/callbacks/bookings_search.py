from dash import Input, Output, State, no_update


def register_bookings_search_callbacks(app, load_data, b_cols):
    @app.callback(
        [Output("b-search", "options"), Output("b-search", "value")],
        [Input("bookings-table-container", "children"), Input("main-tabs", "active_tab")],
        State("b-search", "value"),
    )
    def update_booking_search_options(_bookings_table, active_tab, current_value):
        if active_tab == "tab-bookings":
            df = load_data("bookings.csv", b_cols)
            booking_id_col = b_cols[0]
            customer_col = b_cols[2] if len(b_cols) > 2 else booking_id_col
            service_col = b_cols[4] if len(b_cols) > 4 else booking_id_col
            status_col = b_cols[11] if len(b_cols) > 11 else None
            options = [
                {
                    "label": (
                        f"{r[customer_col]} ({r[booking_id_col]}) - {r[service_col]}"
                        if status_col is None
                        else f"{r[customer_col]} ({r[booking_id_col]}) - {r[service_col]} [{r[status_col]}]"
                    ),
                    "value": r[booking_id_col],
                }
                for _, r in df.iterrows()
            ]
            valid_values = {opt["value"] for opt in options}
            next_value = current_value if current_value in valid_values else None
            return options, next_value
        return no_update, no_update

    @app.callback(
        [Output("btn-edit-booking", "disabled"), Output("btn-delete-booking", "disabled")],
        Input("b-search", "value"),
    )
    def enable_booking_actions(val):
        return (False, False) if val else (True, True)
