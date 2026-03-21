from dash import Input, Output, State, no_update


def register_customers_search_callbacks(app, load_data, c_cols):
    @app.callback(
        [Output("c-search", "options"), Output("c-search", "value")],
        [Input("customers-table-container", "children"), Input("main-tabs", "active_tab")],
        State("c-search", "value"),
    )
    def update_customer_search_options(_customers_table, active_tab, current_value):
        if active_tab == "tab-customers":
            df = load_data("customers.csv", c_cols)
            customer_id_col = c_cols[0]
            bride_name_col = c_cols[2]
            phone1_col = c_cols[5]
            options = [
                {
                    "label": f"{r[bride_name_col]} ({r[phone1_col]})",
                    "value": r[customer_id_col],
                }
                for _, r in df.iterrows()
            ]
            valid_values = {opt["value"] for opt in options}
            next_value = current_value if current_value in valid_values else None
            return options, next_value
        return no_update, no_update

    @app.callback(
        [Output("btn-edit-customer", "disabled"), Output("btn-delete-customer", "disabled")],
        Input("c-search", "value"),
    )
    def enable_customer_actions(val):
        return (False, False) if val else (True, True)
