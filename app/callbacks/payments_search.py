from dash import Input, Output, State, no_update


def register_payments_search_callbacks(app, load_data, p_cols):
    @app.callback(
        [Output("p-search", "options"), Output("p-search", "value")],
        [Input("payments-table-container", "children"), Input("main-tabs", "active_tab")],
        State("p-search", "value"),
    )
    def update_payment_search_options(_payments_table, active_tab, current_value):
        if active_tab == "tab-payments":
            df = load_data("payments.csv", p_cols)
            payment_id_col = p_cols[0]
            customer_name_col = p_cols[4] if len(p_cols) > 4 else payment_id_col
            options = [
                {
                    "label": f"{r[payment_id_col]} - {r[customer_name_col]} ({r[payment_id_col]})",
                    "value": r[payment_id_col],
                }
                for _, r in df.iterrows()
            ]
            valid_values = {opt["value"] for opt in options}
            next_value = current_value if current_value in valid_values else None
            return options, next_value
        return no_update, no_update

    @app.callback(
        [Output("btn-edit-payment", "disabled"), Output("btn-delete-payment", "disabled")],
        Input("p-search", "value"),
    )
    def enable_payment_actions(val):
        return (False, False) if val else (True, True)
