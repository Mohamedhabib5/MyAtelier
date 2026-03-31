from datetime import date
from dash import Input, Output, State, ctx
from app.callbacks.bookings_form_helpers import (
    build_booking_edit_context,
    build_booking_error_alert,
    build_booking_manage_default_result,
    execute_booking_save,
    load_booking_form_seed_data,
)
from app.callbacks.bookings_form_results import (
    build_booking_add_modal_result,
    build_booking_delete_issue_result,
    build_booking_delete_success_result,
    build_booking_edit_modal_result,
    build_booking_missing_fields_result,
    build_booking_save_error_result,
    build_booking_save_success_result,
)
def register_bookings_form_core_callbacks(
    app,
    load_data,
    c_cols,
    s_cols,
    d_cols,
    b_cols,
    is_dresses_dept,
    normalize_code,
    get_bookings_table_content,
    get_dresses_table_content,
    get_payments_table_content,
    logic_module,
    delete_reason,
):
    @app.callback(
        [
            Output("modal-booking", "is_open"),
            Output("b-modal-title", "children"),
            Output("b-dept", "value", allow_duplicate=True),
            Output("b-customer", "value", allow_duplicate=True),
            Output("b-service", "value", allow_duplicate=True),
            Output("b-dress", "value", allow_duplicate=True),
            Output("b-event-date", "date"),
            Output("b-price", "value"),
            Output("b-paid", "value"),
            Output("b-notes", "value"),
            Output("b-date", "date"),
            Output("b-edit-id", "data"),
            Output("modal-delete-booking", "is_open"),
            Output("b-customer", "options", allow_duplicate=True),
            Output("b-service", "options", allow_duplicate=True),
            Output("b-dress", "options", allow_duplicate=True),
            Output("dress-section", "style", allow_duplicate=True),
            Output("b-alert", "children"),
            Output("bookings-table-container", "children"),
            Output("b-search", "value", allow_duplicate=True),
            Output("app-success-toast", "children", allow_duplicate=True),
            Output("app-success-toast", "is_open", allow_duplicate=True),
        ],
        [
            Input("btn-add-booking-modal", "n_clicks"),
            Input("btn-edit-booking", "n_clicks"),
            Input("btn-save-booking", "n_clicks"),
            Input("btn-delete-booking", "n_clicks"),
            Input("btn-cancel-delete-b", "n_clicks"),
            Input("btn-confirm-delete-b", "n_clicks"),
        ],
        [
            State("modal-booking", "is_open"),
            State("b-search", "value"),
            State("modal-delete-booking", "is_open"),
            State("main-tabs", "active_tab"),
            State("b-dept", "value"),
            State("b-customer", "value"),
            State("b-service", "value"),
            State("b-dress", "value"),
            State("b-event-date", "date"),
            State("b-price", "value"),
            State("b-paid", "value"),
            State("b-status", "value"),
            State("b-notes", "value"),
            State("b-date", "date"),
            State("b-edit-id", "data"),
            State("btn-edit-booking", "n_clicks_timestamp"),
            State("btn-save-booking", "n_clicks_timestamp"),
            State("btn-delete-booking", "n_clicks_timestamp"),
            State("btn-cancel-delete-b", "n_clicks_timestamp"),
            State("btn-confirm-delete-b", "n_clicks_timestamp"),
            State("btn-add-booking-modal", "n_clicks_timestamp"),
            State("user_session_store", "data"),
            State("viewport-mode", "data"),
        ],
        prevent_initial_call=True,
    )
    def manage_bookings(
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
        fit_dept,
        fit_cust,
        fit_service,
        fit_dress,
        fit_event_date,
        fit_price,
        fit_paid,
        fit_status,
        fit_notes,
        fit_book_date,
        edit_id,
        edit_click_ts,
        save_click_ts,
        del_click_ts,
        cancel_click_ts,
        confirm_click_ts,
        add_click_ts,
        session_data,
        viewport_mode,
    ):
        triggered_val = None
        if getattr(ctx, "triggered", None):
            triggered_val = ctx.triggered[0].get("value")
        if not isinstance(triggered_val, (int, float)) or triggered_val <= 0:
            return build_booking_manage_default_result(False, False)
        ctx_id = ctx.triggered_id
        login_ts = 0
        if isinstance(session_data, dict):
            try:
                login_ts = float(session_data.get("login_ts") or 0)
            except Exception:
                login_ts = 0
        ts_map = {
            "btn-add-booking-modal": add_click_ts,
            "btn-edit-booking": edit_click_ts,
            "btn-save-booking": save_click_ts,
            "btn-delete-booking": del_click_ts,
            "btn-cancel-delete-b": cancel_click_ts,
            "btn-confirm-delete-b": confirm_click_ts,
        }
        try:
            trigger_ts = float(ts_map.get(ctx_id) or 0)
        except Exception:
            trigger_ts = 0
        if ctx_id in ts_map and login_ts > 0 and trigger_ts > 0 and trigger_ts < login_ts:
            return build_booking_manage_default_result(False, False)
        seed_data = load_booking_form_seed_data(load_data, c_cols, d_cols, s_cols)
        c_opts = seed_data["customer_options"]
        d_opts = seed_data["dress_options"]
        s_df = seed_data["services_df"]
        if ctx_id == "btn-add-booking-modal" and n_add and active_tab == "tab-bookings":
            today_iso = date.today().isoformat()
            return build_booking_add_modal_result(c_opts, d_opts, today_iso)
        if ctx_id == "btn-edit-booking" and n_edit and active_tab == "tab-bookings" and search_val:
            df = load_data("bookings.csv", b_cols)
            row = df[df[b_cols[0]] == search_val]
            if not row.empty:
                record = row.iloc[0]
                edit_context = build_booking_edit_context(
                    record,
                    b_cols,
                    s_df,
                    s_cols,
                    d_opts,
                    normalize_code,
                    is_dresses_dept,
                )
                return build_booking_edit_modal_result(record, b_cols, search_val, c_opts, edit_context)
        if ctx_id == "btn-save-booking" and n_save and active_tab == "tab-bookings":
            if not fit_cust or not fit_service or not fit_price:
                return build_booking_missing_fields_result()
            save_result = execute_booking_save(
                logic_module,
                edit_id,
                fit_cust,
                fit_dept,
                fit_service,
                fit_dress,
                fit_event_date,
                fit_price,
                fit_paid,
                fit_status,
                fit_notes,
                fit_book_date,
                is_dresses_dept,
            )
            if save_result["success"]:
                today_iso = date.today().isoformat()
                return build_booking_save_success_result(
                    save_result["mode"],
                    today_iso,
                    get_bookings_table_content(viewport_mode=viewport_mode),
                )
            return build_booking_save_error_result(
                build_booking_error_alert(save_result["msg"], "يوجد حجز لهذا الفستان في نفس اليوم")
            )
        if ctx_id == "btn-delete-booking" and n_del and active_tab == "tab-bookings":
            return build_booking_manage_default_result(False, True)
        if ctx_id == "btn-confirm-delete-b" and n_confirm and active_tab == "tab-bookings":
            if search_val:
                ok, msg = logic_module.delete_booking(search_val)
                if ok:
                    return build_booking_delete_success_result(
                        get_bookings_table_content(viewport_mode=viewport_mode)
                    )
                alert = build_booking_error_alert(
                    delete_reason(msg),
                    "لا يمكن حذف الحجز",
                )
                return build_booking_delete_issue_result(
                    alert,
                    get_bookings_table_content(viewport_mode=viewport_mode),
                )
            warning_alert = build_booking_error_alert("", "اختر حجزًا قبل الحذف")
            return build_booking_delete_issue_result(
                warning_alert,
                get_bookings_table_content(viewport_mode=viewport_mode),
            )
        if ctx_id == "btn-cancel-delete-b" and n_cancel and active_tab == "tab-bookings":
            return build_booking_manage_default_result(False, False)
        return build_booking_manage_default_result(is_open, is_del_open)
