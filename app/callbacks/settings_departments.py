import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, no_update

import logic
from app.callbacks.feedback import success_toast


def build_dept_table_content(check_departments, create_dt):
    df = check_departments()
    if df.empty:
        return dbc.Alert("\u0644\u0627 \u064a\u0648\u062c\u062f \u0623\u0642\u0633\u0627\u0645", color="info")
    return create_dt(df, "dept-table", "departments.csv")


def register_settings_departments_callbacks(
    app,
    check_departments,
    load_data,
    s_cols,
    b_cols,
    get_dept_table_content,
):
    @app.callback(
        Output("company-name-input", "value"),
        Input("main-tabs", "active_tab"),
    )
    def load_company_name(active_tab):
        if active_tab == "tab-settings":
            return logic.get_company_name()
        return no_update

    @app.callback(
        [
            Output("company-name-alert", "children"),
            Output("app-title-desktop", "children"),
            Output("app-title-mobile", "children"),
        ],
        Input("btn-save-company-name", "n_clicks"),
        State("company-name-input", "value"),
        prevent_initial_call=True,
    )
    def save_company_name(_n_clicks, company_name):
        ok, msg, saved_value = logic.set_company_name(company_name)
        if ok:
            return dbc.Alert(msg, color="success"), saved_value, saved_value
        return dbc.Alert(msg, color="warning"), no_update, no_update

    @app.callback(
        [Output("dept-search", "options"), Output("dept-search", "value")],
        [Input("dept-table-container", "children"), Input("main-tabs", "active_tab")],
        State("dept-search", "value"),
    )
    def update_dept_search(_, active_tab, current_value):
        if active_tab == "tab-settings":
            df = check_departments()
            options = [
                {"label": r["department_name"], "value": r["department_name"]}
                for _, r in df.iterrows()
            ]
            valid_values = {opt["value"] for opt in options}
            next_value = current_value if current_value in valid_values else None
            return options, next_value
        return no_update, no_update

    @app.callback(
        [Output("btn-edit-dept", "disabled"), Output("btn-delete-dept", "disabled")],
        Input("dept-search", "value"),
    )
    def enable_dept_actions(val):
        return (False, False) if val else (True, True)

    @app.callback(
        [
            Output("modal-dept", "is_open"),
            Output("dept-modal-title", "children"),
            Output("dept-name", "value"),
            Output("dept-edit-id", "data"),
            Output("modal-delete-dept", "is_open"),
        ],
        [
            Input("btn-add-dept-modal", "n_clicks"),
            Input("btn-edit-dept", "n_clicks"),
            Input("btn-save-dept", "n_clicks"),
            Input("btn-delete-dept", "n_clicks"),
            Input("btn-cancel-delete-dept", "n_clicks"),
            Input("btn-confirm-delete-dept", "n_clicks"),
        ],
        [
            State("modal-dept", "is_open"),
            State("dept-search", "value"),
            State("modal-delete-dept", "is_open"),
        ],
        prevent_initial_call=True,
    )
    def handle_dept_modals(
        _n_add,
        _n_edit,
        _n_save,
        _n_del,
        _n_cancel,
        _n_confirm,
        is_open,
        search_val,
        is_del_open,
    ):
        ctx_id = ctx.triggered_id

        if ctx_id == "btn-add-dept-modal":
            return True, "\u0625\u0636\u0627\u0641\u0629 \u0642\u0633\u0645 \u062c\u062f\u064a\u062f", "", None, False

        if ctx_id == "btn-edit-dept" and search_val:
            return True, f"\u062a\u0639\u062f\u064a\u0644 \u0642\u0633\u0645: {search_val}", search_val, search_val, False

        if ctx_id == "btn-save-dept":
            return False, no_update, no_update, None, False
        if ctx_id == "btn-delete-dept":
            return False, no_update, no_update, no_update, True
        if ctx_id in ["btn-confirm-delete-dept", "btn-cancel-delete-dept"]:
            return False, no_update, no_update, no_update, False

        return is_open, no_update, no_update, no_update, is_del_open

    @app.callback(
        [
            Output("dept-alert", "children"),
            Output("dept-table-container", "children"),
            Output("dept-search", "value", allow_duplicate=True),
            Output("app-success-toast", "children", allow_duplicate=True),
            Output("app-success-toast", "is_open", allow_duplicate=True),
        ],
        [Input("btn-save-dept", "n_clicks"), Input("btn-confirm-delete-dept", "n_clicks")],
        [State("dept-name", "value"), State("dept-edit-id", "data"), State("dept-search", "value")],
        prevent_initial_call=True,
    )
    def save_or_delete_department(_n_save, _n_del, name, edit_id, search_val):
        ctx_id = ctx.triggered_id
        df = check_departments()

        # Load dependencies to check usage
        s_df = load_data("services.csv", s_cols)
        b_df = load_data("bookings.csv", b_cols)
        svc_dept_col = s_cols[1] if len(s_cols) > 1 else None
        book_dept_col = b_cols[3] if len(b_cols) > 3 else None

        # --- DELETE ---
        if ctx_id == "btn-confirm-delete-dept" and search_val:
            is_used = False
            if svc_dept_col and not s_df.empty and svc_dept_col in s_df.columns and search_val in s_df[svc_dept_col].values:
                is_used = True
            if book_dept_col and not b_df.empty and book_dept_col in b_df.columns and search_val in b_df[book_dept_col].values:
                is_used = True

            if is_used:
                return (
                    dbc.Alert(
                        f"\u274c \u0644\u0627 \u064a\u0645\u0643\u0646 \u062d\u0630\u0641 \u0627\u0644\u0642\u0633\u0645 '{search_val}' \u0644\u0623\u0646\u0647 \u0645\u0631\u062a\u0628\u0637 \u0628\u062e\u062f\u0645\u0627\u062a \u0623\u0648 \u062d\u062c\u0648\u0632\u0627\u062a \u0645\u0633\u062c\u0644\u0629.",
                        color="danger",
                    ),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            ok, _ = logic.delete_department(search_val)
            if ok:
                return (
                    "",
                    get_dept_table_content(),
                    None,
                    *success_toast("\u2705 \u062a\u0645 \u062d\u0630\u0641 \u0627\u0644\u0642\u0633\u0645"),
                )
            return (
                dbc.Alert("\u274c \u0644\u0645 \u064a\u062a\u0645 \u0627\u0644\u0639\u062b\u0648\u0631 \u0639\u0644\u0649 \u0627\u0644\u0642\u0633\u0645", color="danger"),
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # --- SAVE ---
        if ctx_id == "btn-save-dept":
            if not name:
                return (
                    dbc.Alert("\u26a0\ufe0f \u0627\u0633\u0645 \u0627\u0644\u0642\u0633\u0645 \u0645\u0637\u0644\u0648\u0628", color="warning"),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            name = name.strip()

            if edit_id:  # Edit
                if edit_id != name and not df.empty and name in df["department_name"].values:
                    return (
                        dbc.Alert("\u26a0\ufe0f \u0647\u0630\u0627 \u0627\u0644\u0627\u0633\u0645 \u0645\u0633\u062a\u062e\u062f\u0645 \u0628\u0627\u0644\u0641\u0639\u0644", color="warning"),
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                    )

                is_used = False
                if svc_dept_col and not s_df.empty and svc_dept_col in s_df.columns and edit_id in s_df[svc_dept_col].values:
                    is_used = True
                if book_dept_col and not b_df.empty and book_dept_col in b_df.columns and edit_id in b_df[book_dept_col].values:
                    is_used = True

                if is_used and edit_id != name:
                    return (
                        dbc.Alert(
                            f"\u274c \u0644\u0627 \u064a\u0645\u0643\u0646 \u062a\u0639\u062f\u064a\u0644 \u0627\u0633\u0645 \u0627\u0644\u0642\u0633\u0645 '{edit_id}' \u0644\u0623\u0646\u0647 \u0645\u0633\u062a\u062e\u062f\u0645 \u0641\u064a \u0627\u0644\u0646\u0638\u0627\u0645.",
                            color="danger",
                        ),
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                    )

                ok, msg = logic.update_department(edit_id, name)
                if ok:
                    return (
                        "",
                        get_dept_table_content(),
                        None,
                        *success_toast("\u2705 \u062a\u0645 \u062a\u0639\u062f\u064a\u0644 \u0627\u0644\u0642\u0633\u0645"),
                    )
                if msg == "Exists":
                    return (
                        dbc.Alert("\u26a0\ufe0f \u0647\u0630\u0627 \u0627\u0644\u0627\u0633\u0645 \u0645\u0633\u062a\u062e\u062f\u0645 \u0628\u0627\u0644\u0641\u0639\u0644", color="warning"),
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                    )
                return (
                    dbc.Alert("\u274c \u062d\u062f\u062b \u062e\u0637\u0623 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u062a\u0639\u062f\u064a\u0644", color="danger"),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            # Add
            if not df.empty and name in df["department_name"].values:
                return (
                    dbc.Alert("\u26a0\ufe0f \u0627\u0644\u0642\u0633\u0645 \u0645\u0648\u062c\u0648\u062f \u0628\u0627\u0644\u0641\u0639\u0644", color="warning"),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            ok, msg = logic.add_department(name)
            if ok:
                return (
                    "",
                    get_dept_table_content(),
                    None,
                    *success_toast("\u2705 \u062a\u0645 \u0625\u0636\u0627\u0641\u0629 \u0627\u0644\u0642\u0633\u0645"),
                )
            if msg == "Exists":
                return (
                    dbc.Alert("\u26a0\ufe0f \u0627\u0644\u0642\u0633\u0645 \u0645\u0648\u062c\u0648\u062f \u0628\u0627\u0644\u0641\u0639\u0644", color="warning"),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )
            return (
                dbc.Alert("\u274c \u062d\u062f\u062b \u062e\u0637\u0623 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u0625\u0636\u0627\u0641\u0629", color="danger"),
                no_update,
                no_update,
                no_update,
                no_update,
            )

        return no_update, no_update, no_update, no_update, no_update
