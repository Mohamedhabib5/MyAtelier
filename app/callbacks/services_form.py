from dash import Input, Output, State, ctx, html, no_update
from app.callbacks.feedback import success_toast
import os


def register_services_form_callbacks(
    app,
    load_data,
    s_cols,
    get_services_table_content,
    logic_module,
    delete_reason,
):
    @app.callback(
        [
            Output("modal-service", "is_open"),
            Output("s-modal-title", "children"),
            Output("s-name", "value"),
            Output("s-dept", "value", allow_duplicate=True),
            Output("s-price", "value"),
            Output("s-edit-id", "data"),
            Output("modal-delete-service", "is_open"),
            Output("s-alert", "children"),
            Output("services-table-container", "children"),
            Output("s-search", "value", allow_duplicate=True),
            Output("app-success-toast", "children", allow_duplicate=True),
            Output("app-success-toast", "is_open", allow_duplicate=True),
        ],
        [
            Input("btn-add-service-modal", "n_clicks"),
            Input("btn-edit-service", "n_clicks"),
            Input("btn-save-service", "n_clicks"),
            Input("btn-delete-service", "n_clicks"),
            Input("btn-cancel-delete-s", "n_clicks"),
            Input("btn-confirm-delete-s", "n_clicks"),
        ],
        [
            State("modal-service", "is_open"),
            State("s-search", "value"),
            State("modal-delete-service", "is_open"),
            State("main-tabs", "active_tab"),
            State("btn-add-service-modal", "n_clicks_timestamp"),
            State("btn-edit-service", "n_clicks_timestamp"),
            State("btn-save-service", "n_clicks_timestamp"),
            State("btn-delete-service", "n_clicks_timestamp"),
            State("btn-cancel-delete-s", "n_clicks_timestamp"),
            State("btn-confirm-delete-s", "n_clicks_timestamp"),
            State("user_session_store", "data"),
            State("s-name", "value"),
            State("s-dept", "value"),
            State("s-price", "value"),
            State("s-edit-id", "data"),
        ],
        prevent_initial_call=True,
    )
    def manage_services(
        n_add,
        n_edit,
        n_save,
        n_del,
        n_cancel,
        n_confirm,
        is_open,
        search_val,
        is_del_open,
        active_tab,
        add_ts,
        edit_ts,
        save_ts,
        del_ts,
        cancel_ts,
        confirm_ts,
        session_data,
        name,
        dept,
        price,
        edit_id,
    ):
        if os.environ.get("APP_TRACE_MODAL_VALUES", "0").strip() in {"1", "true", "yes"}:
            try:
                print("[TRACE][services]", "ctx_id=", ctx.triggered_id, "triggered=", getattr(ctx, "triggered", None), "n_add=", n_add, "n_edit=", n_edit, "n_save=", n_save, "n_del=", n_del, "active_tab=", active_tab)
            except Exception:
                pass

        triggered_val = None
        if getattr(ctx, "triggered", None):
            triggered_val = ctx.triggered[0].get("value")
        if not isinstance(triggered_val, (int, float)) or triggered_val <= 0:
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        ctx_id = ctx.triggered_id
        login_ts = 0
        if isinstance(session_data, dict):
            try:
                login_ts = float(session_data.get("login_ts") or 0)
            except Exception:
                login_ts = 0
        ts_map = {
            "btn-add-service-modal": add_ts,
            "btn-edit-service": edit_ts,
            "btn-save-service": save_ts,
            "btn-delete-service": del_ts,
            "btn-cancel-delete-s": cancel_ts,
            "btn-confirm-delete-s": confirm_ts,
        }
        try:
            trigger_ts = float(ts_map.get(ctx_id) or 0)
        except Exception:
            trigger_ts = 0
        if ctx_id in ts_map and login_ts > 0 and trigger_ts > 0 and trigger_ts < login_ts:
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 1. Add
        if ctx_id == "btn-add-service-modal" and n_add and active_tab == "tab-services":
            return (
                True,
                "\u0625\u0636\u0627\u0641\u0629 \u062e\u062f\u0645\u0629 \u062c\u062f\u064a\u062f\u0629",
                "",
                None,
                None,
                None,
                False,
                "",
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 2. Edit
        if ctx_id == "btn-edit-service" and n_edit and active_tab == "tab-services" and search_val:
            df = load_data("services.csv", s_cols)
            row = df[df[s_cols[0]] == search_val]
            if not row.empty:
                r = row.iloc[0]
                return (
                    True,
                    f"تعديل خدمة: {r[s_cols[2]]}",
                    r[s_cols[2]],
                    r[s_cols[1]],
                    r[s_cols[3]],
                    search_val,
                    False,
                    "",
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

        # 3. Save
        if ctx_id == "btn-save-service" and n_save and active_tab == "tab-services":
            if not name:
                return (
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    dbc.Alert("⚠️ الاسم مطلوب", color="warning"),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            if edit_id:  # Edit
                success, msg = logic_module.update_service(edit_id, name, dept, price)
                if success:
                    return (
                        False,
                        no_update,
                        "",
                        None,
                        None,
                        None,
                        False,
                        "",
                        get_services_table_content(),
                        None,
                        *success_toast(f"\\u2705 {msg}"),
                    )
                return (
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    dbc.Alert(f"❌ {msg}", color="danger"),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            # Add
            success, msg, _new_id = logic_module.add_service(name, dept, price)
            if success:
                return (
                    False,
                    no_update,
                    "",
                    None,
                    None,
                    None,
                    False,
                    "",
                    get_services_table_content(),
                    None,
                    *success_toast(f"\\u2705 {msg}"),
                )
            return (
                True,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                dbc.Alert(f"❌ {msg}", color="danger"),
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 4. Delete Open
        if ctx_id == "btn-delete-service" and n_del and active_tab == "tab-services":
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                True,
                "",
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 5. Confirm Delete
        if ctx_id == "btn-confirm-delete-s" and n_confirm and active_tab == "tab-services":
            if search_val:
                ok, msg = logic_module.delete_service(search_val)
                if ok:
                    return (
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        False,
                        "",
                        get_services_table_content(),
                        None,
                        *success_toast("\\u2705 \\u062a\\u0645 \\u062d\\u0630\\u0641 \\u0627\\u0644\\u062e\\u062f\\u0645\\u0629 \\u0628\\u0646\\u062c\\u0627\\u062d"),
                    )
                alert = dbc.Alert(f"❌ لا يمكن حذف الخدمة: {delete_reason(msg)}", color="danger")
                return (
                    False,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    "",
                    html.Div([alert, get_services_table_content()]),
                    no_update,
                    no_update,
                    no_update,
                )
            warning_alert = dbc.Alert("⚠️ اختر خدمة قبل الحذف", color="warning")
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                "",
                html.Div([warning_alert, get_services_table_content()]),
                no_update,
                no_update,
                no_update,
            )

        # 6. Cancel Delete
        if ctx_id == "btn-cancel-delete-s" and n_cancel and active_tab == "tab-services":
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                "",
                no_update,
                no_update,
                no_update,
                no_update,
            )

        return (
            is_open,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            is_del_open,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

