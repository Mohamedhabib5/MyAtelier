from dash import Input, Output, State, no_update
import logic


def register_services_search_callbacks(app, load_data, s_cols):
    @app.callback(
        [Output("s-dept", "options"), Output("s-dept", "value")],
        [Input("dept-table-container", "children"), Input("main-tabs", "active_tab")],
        State("s-dept", "value"),
    )
    def update_service_department_options(_dept_table, _active_tab, current_value):
        df = logic.check_departments()
        if df.empty or "department_name" not in df.columns:
            return [], None

        seen = set()
        options = []
        for raw_name in df["department_name"].tolist():
            name = str(raw_name).strip()
            if not name or name in seen:
                continue
            seen.add(name)
            options.append({"label": name, "value": name})
        valid_values = {opt["value"] for opt in options}
        next_value = current_value if current_value in valid_values else None
        return options, next_value

    @app.callback(
        [Output("s-search", "options"), Output("s-search", "value")],
        [Input("services-table-container", "children"), Input("main-tabs", "active_tab")],
        State("s-search", "value"),
    )
    def update_service_search_options(_services_table, active_tab, current_value):
        if active_tab == "tab-services":
            df = load_data("services.csv", s_cols)
            service_id_col = s_cols[0]
            service_name_col = s_cols[2] if len(s_cols) > 2 else service_id_col
            options = [
                {
                    "label": f"{r[service_name_col]} ({r[service_id_col]})",
                    "value": r[service_id_col],
                }
                for _, r in df.iterrows()
            ]
            valid_values = {opt["value"] for opt in options}
            next_value = current_value if current_value in valid_values else None
            return options, next_value
        return no_update, no_update

    @app.callback(
        [Output("btn-edit-service", "disabled"), Output("btn-delete-service", "disabled")],
        Input("s-search", "value"),
    )
    def enable_service_actions(val):
        return (False, False) if val else (True, True)
