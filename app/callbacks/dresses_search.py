from dash import Input, Output, State, no_update


def register_dresses_search_callbacks(app, load_data, d_cols):
    @app.callback(
        [Output("d-search", "options"), Output("d-search", "value")],
        [Input("dresses-table-container", "children"), Input("main-tabs", "active_tab")],
        State("d-search", "value"),
    )
    def update_dress_search_options(_dresses_table, active_tab, current_value):
        if active_tab == "tab-dresses":
            df = load_data("dresses.csv", d_cols)
            dress_code_col = d_cols[0]
            dress_desc_col = d_cols[3] if len(d_cols) > 3 else dress_code_col
            options = [
                {
                    "label": f"{r[dress_code_col]} ({r[dress_desc_col]})",
                    "value": r[dress_code_col],
                }
                for _, r in df.iterrows()
            ]
            valid_values = {opt["value"] for opt in options}
            next_value = current_value if current_value in valid_values else None
            return options, next_value
        return no_update, no_update

    @app.callback(
        [Output("btn-edit-dress", "disabled"), Output("btn-delete-dress", "disabled")],
        Input("d-search", "value"),
    )
    def enable_dress_actions(val):
        return (False, False) if val else (True, True)
