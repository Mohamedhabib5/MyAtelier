from datetime import date
import os

from dash import Input, Output, State, ctx, html, no_update
import dash_bootstrap_components as dbc
from app.callbacks.feedback import success_toast

def build_booking_customer_options(c_df, c_cols):
    if c_df.empty:
        return []

    bride_col = c_cols[2] if len(c_cols) > 2 else c_cols[0]
    groom_col = c_cols[3] if len(c_cols) > 3 else bride_col
    return [
        {"label": f"{r[bride_col]} | {r[groom_col]}", "value": r[bride_col]}
        for _, r in c_df.iterrows()
    ]


def build_booking_dress_options(d_df, d_cols):
    if d_df.empty:
        return []

    code_col = d_cols[0]
    desc_col = d_cols[3] if len(d_cols) > 3 else code_col
    status_col = d_cols[5] if len(d_cols) > 5 else None
    options = []
    for _, row in d_df.iterrows():
        code = row[code_col]
        if status_col is None:
            label = f"{code} | {row[desc_col]}"
        else:
            label = f"{code} | {row[desc_col]} ({row[status_col]})"
        options.append({"label": label, "value": code})
    return options


def load_booking_form_seed_data(load_data, c_cols, d_cols, s_cols):
    c_df = load_data("customers.csv", c_cols)
    d_df = load_data("dresses.csv", d_cols)
    s_df = load_data("services.csv", s_cols)

    return {
        "customers_df": c_df,
        "dresses_df": d_df,
        "services_df": s_df,
        "customer_options": build_booking_customer_options(c_df, c_cols),
        "dress_options": build_booking_dress_options(d_df, d_cols),
    }


def build_booking_service_options_for_dept(s_df, s_cols, dept):
    if not dept or s_df.empty:
        return []

    dept_col = s_cols[1] if len(s_cols) > 1 else s_cols[0]
    service_name_col = s_cols[2] if len(s_cols) > 2 else s_cols[0]
    service_price_col = s_cols[3] if len(s_cols) > 3 else None

    s_filtered = s_df[s_df[dept_col].astype(str).str.strip() == str(dept).strip()]
    options = []
    for _, row in s_filtered.iterrows():
        service_name = str(row[service_name_col]).strip()
        if not service_name:
            continue
        if service_price_col is None:
            label = service_name
        else:
            label = f"{service_name} ({row[service_price_col]})"
        options.append({"label": label, "value": service_name})
    return options


def ensure_booking_service_option(service_options, current_service):
    value = str(current_service or "").strip()
    if not value:
        return service_options
    if value in {opt["value"] for opt in service_options}:
        return service_options
    return service_options + [{"label": f"{value} (missing)", "value": value}]


def ensure_booking_dress_option(dress_options, current_dress, normalize_code):
    value = str(current_dress or "").strip()
    normalized = normalize_code(value)
    if not normalized:
        return dress_options

    existing = {normalize_code(opt["value"]) for opt in dress_options}
    if normalized in existing:
        return dress_options
    return dress_options + [{"label": f"{value} (missing)", "value": value}]


def build_booking_edit_context(
    row,
    b_cols,
    s_df,
    s_cols,
    dress_options,
    normalize_code,
    is_dresses_dept,
):
    curr_dept = row[b_cols[3]]
    service_options = build_booking_service_options_for_dept(s_df, s_cols, curr_dept)
    dress_style = {"display": "block"} if is_dresses_dept(curr_dept) else {"display": "none"}

    curr_service = row[b_cols[4]]
    service_options = ensure_booking_service_option(service_options, curr_service)

    curr_dress = row[b_cols[5]]
    dress_options = ensure_booking_dress_option(dress_options, curr_dress, normalize_code)

    return {
        "dept": curr_dept,
        "service_options": service_options,
        "dress_options": dress_options,
        "dress_style": dress_style,
    }


def build_booking_error_alert(msg, fallback):
    text = (msg or "").strip()
    if not text or text in ("Dress Taken",):
        text = fallback
    return dbc.Alert(text, color="danger")


def execute_booking_delete(logic_module, search_val):
    if not search_val:
        return {"has_search": False}

    ok, msg = logic_module.delete_booking(search_val)
    return {"has_search": True, "ok": ok, "msg": msg}


def build_booking_delete_callback_result(delete_result, get_bookings_table_content, error_alert=None):
    if delete_result["has_search"]:
        if delete_result["ok"]:
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
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
                "",
                get_bookings_table_content(),
                None,
                None,
            )
        table_content = (
            html.Div([error_alert, get_bookings_table_content()])
            if error_alert is not None
            else get_bookings_table_content()
        )
        return (
            False,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
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
            "",
            table_content,
            no_update,
            no_update,
        )
    return (
        False,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
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
        "",
        no_update,
        no_update,
        no_update,
    )


def build_booking_delete_toggle_result(marker_value):
    return (
        False,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        marker_value,
        no_update,
        no_update,
        no_update,
        no_update,
        "",
        no_update,
        no_update,
        no_update,
    )


def execute_booking_confirm_delete(
    logic_module,
    search_val,
    get_bookings_table_content,
    build_error_alert=None,
):
    delete_result = execute_booking_delete(logic_module, search_val)
    if (
        delete_result["has_search"]
        and not delete_result["ok"]
        and build_error_alert is not None
    ):
        return build_booking_delete_callback_result(
            delete_result,
            get_bookings_table_content,
            error_alert=build_error_alert(delete_result["msg"]),
        )
    return build_booking_delete_callback_result(
        delete_result,
        get_bookings_table_content,
    )


def build_booking_save_callback_result(
    mode,
    success,
    get_bookings_table_content,
    error_alert=None,
    today_iso=None,
):
    if mode == "edit":
        if success:
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                None,
                None,
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                "",
                get_bookings_table_content(),
                None,
            )
        return (
            True,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
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
            error_alert if error_alert is not None else no_update,
            no_update,
            no_update,
            no_update,
        )

    if success:
        safe_today = today_iso or ""
        return (
            False,
            no_update,
            None,
            None,
            None,
            None,
            safe_today,
            "",
            "",
            "",
            safe_today,
            None,
            False,
            no_update,
            no_update,
            no_update,
            no_update,
            "",
            get_bookings_table_content(),
            None,
        )

    return (
        True,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
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
        error_alert if error_alert is not None else no_update,
        no_update,
        no_update,
        no_update,
    )


def build_booking_save_required_fields_result(validation_alert):
    return (
        True,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
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
        validation_alert if validation_alert is not None else no_update,
        no_update,
        no_update,
    )


def build_booking_manage_default_result(
    is_open,
    is_del_open,
    alert_out=no_update,
    table_out=no_update,
    search_out=no_update,
    toast_msg=no_update,
    toast_is_open=no_update,
):
    return (
        is_open,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
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
        alert_out,
        table_out,
        search_out,
        toast_msg,
        toast_is_open,
    )


def build_booking_add_modal_result(*result_values):
    return tuple(result_values)


def build_booking_edit_modal_result(*result_values):
    return tuple(result_values)


def execute_booking_save(
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
):
    dress_val = fit_dress if (is_dresses_dept(fit_dept) and fit_dress) else "-"

    if edit_id:
        success, msg = logic_module.update_booking(
            edit_id,
            fit_cust,
            fit_dept,
            fit_service,
            dress_val,
            fit_event_date,
            fit_price,
            fit_paid,
            fit_status,
            fit_notes,
        )
        return {"mode": "edit", "success": success, "msg": msg, "dress_val": dress_val}

    success, msg, new_id = logic_module.add_booking(
        fit_cust,
        fit_dept,
        fit_service,
        dress_val,
        fit_event_date,
        fit_price,
        fit_paid,
        fit_status,
        fit_notes,
        reg_date=fit_book_date,
    )
    return {"mode": "add", "success": success, "msg": msg, "new_id": new_id, "dress_val": dress_val}


def register_bookings_form_callbacks(
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
    ):
        if os.environ.get("APP_TRACE_MODAL_HYDRATION", "0").strip() in {"1", "true", "yes"}:
            try:
                print("[TRACE][bookings.manage_bookings]", "triggered_id=", ctx.triggered_id, "triggered=", ctx.triggered, "triggered_prop_ids=", getattr(ctx, "triggered_prop_ids", {}))
            except Exception:
                pass

        if os.environ.get("APP_TRACE_MODAL_VALUES", "0").strip() in {"1", "true", "yes"}:
            try:
                print("[TRACE][bookings]", "ctx_id=", ctx.triggered_id, "triggered=", getattr(ctx, "triggered", None), "n_add=", n_add, "n_edit=", n_edit, "n_save=", n_save, "n_del=", n_del, "active_tab=", active_tab)
            except Exception:
                pass

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

        # Load options
        c_df = load_data("customers.csv", c_cols)
        c_opts = [
            {"label": f"{r[c_cols[2]]} | {r[c_cols[3]]}", "value": r[c_cols[2]]}
            for _, r in c_df.iterrows()
        ]
        d_df = load_data("dresses.csv", d_cols)
        d_opts = [
            {
                "label": f"{r[d_cols[0]]} | {r[d_cols[3]]} ({r[d_cols[5]]})",
                "value": r[d_cols[0]],
            }
            for _, r in d_df.iterrows()
        ]
        s_df = load_data("services.csv", s_cols)

        # 1. Add
        add_ts = 0
        try:
            add_ts = float(add_click_ts or 0)
        except Exception:
            add_ts = 0

        if (
            ctx_id == "btn-add-booking-modal"
            and n_add
            and active_tab == "tab-bookings"
        ):
            return (
                True,
                "\u062a\u0633\u062c\u064a\u0644 \u062d\u062c\u0632 \u062c\u062f\u064a\u062f",
                None,
                None,
                None,
                None,
                date.today().isoformat(),
                None,
                None,
                "",
                date.today().isoformat(),
                None,
                False,
                c_opts,
                [],
                d_opts,
                {"display": "none"},
                "",
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 2. Edit
        if ctx_id == "btn-edit-booking" and n_edit and active_tab == "tab-bookings" and search_val:
            df = load_data("bookings.csv", b_cols)
            row = df[df[b_cols[0]] == search_val]
            if not row.empty:
                r = row.iloc[0]
                curr_dept = r[b_cols[3]]
                s_filtered = s_df[s_df[s_cols[1]] == curr_dept] if not s_df.empty else s_df
                s_opts = [
                    {
                        "label": f"{service_row[s_cols[2]]} ({service_row[s_cols[3]]}\u062c)",
                        "value": service_row[s_cols[2]],
                    }
                    for _, service_row in s_filtered.iterrows()
                ]
                d_style = {"display": "block"} if is_dresses_dept(curr_dept) else {"display": "none"}

                # Ensure current values exist in options (handle missing references)
                curr_service = r[b_cols[4]]
                if curr_service and curr_service not in {opt["value"] for opt in s_opts}:
                    s_opts = s_opts + [{"label": f"{curr_service} (\u063a\u064a\u0631 \u0645\u0648\u062c\u0648\u062f)", "value": curr_service}]

                curr_dress = r[b_cols[5]]
                norm_values = {normalize_code(opt["value"]) for opt in d_opts}
                if normalize_code(curr_dress) and normalize_code(curr_dress) not in norm_values:
                    d_opts = d_opts + [{"label": f"{curr_dress} (\u063a\u064a\u0631 \u0645\u0648\u062c\u0648\u062f)", "value": curr_dress}]

                return (
                    True,
                    f"\u062a\u0639\u062f\u064a\u0644 \u062d\u062c\u0632: {r[b_cols[0]]}",
                    r[b_cols[3]],
                    r[b_cols[2]],
                    r[b_cols[4]],
                    r[b_cols[5]],
                    r[b_cols[6]],
                    r[b_cols[7]],
                    r[b_cols[8]],
                    r[b_cols[10]],
                    r[b_cols[1]],
                    search_val,
                    False,
                    c_opts,
                    s_opts,
                    d_opts,
                    d_style,
                    "",
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

        # 3. Save
        if ctx_id == "btn-save-booking" and n_save and active_tab == "tab-bookings":
            def _booking_alert_text(msg, fallback="\u064a\u0648\u062c\u062f \u062d\u062c\u0632 \u0644\u0647\u0630\u0627 \u0627\u0644\u0641\u0633\u062a\u0627\u0646 \u0641\u064a \u0646\u0641\u0633 \u0627\u0644\u064a\u0648\u0645"):
                text = (msg or "").strip()
                # Normalize legacy + canonical conflict outputs to one explicit user message.
                if text in ("Dress Taken", "\u0627\u0644\u0641\u0633\u062a\u0627\u0646 \u0645\u062d\u062c\u0648\u0632 \u0628\u0647\u0630\u0627 \u0627\u0644\u062a\u0627\u0631\u064a\u062e"):
                    text = fallback
                if not text:
                    text = fallback
                return text

            def _booking_alert(msg):
                return dbc.Alert(_booking_alert_text(msg), color="danger")

            if not fit_cust or not fit_service or not fit_price:
                return (
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
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
                    dbc.Alert("\u26a0\ufe0f \u0628\u064a\u0627\u0646\u0627\u062a \u0646\u0627\u0642\u0635\u0629", color="warning"),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            dress_val = fit_dress if (is_dresses_dept(fit_dept) and fit_dress) else "-"

            if edit_id:  # Edit
                success, msg = logic_module.update_booking(
                    edit_id,
                    fit_cust,
                    fit_dept,
                    fit_service,
                    dress_val,
                    fit_event_date,
                    fit_price,
                    fit_paid,
                    fit_status,
                    fit_notes,
                )
                if success:
                    return (
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        None,
                        None,
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        "",
                        get_bookings_table_content(),
                        None,
                        *success_toast("تم تعديل الحجز بنجاح"),
                    )
                return (
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
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
                    _booking_alert(msg),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            # Add
            success, msg, _new_id = logic_module.add_booking(
                fit_cust,
                fit_dept,
                fit_service,
                dress_val,
                fit_event_date,
                fit_price,
                fit_paid,
                fit_status,
                fit_notes,
                reg_date=fit_book_date,
            )
            if success:
                return (
                    False,
                    no_update,
                    None,
                    None,
                    None,
                    None,
                    date.today().isoformat(),
                    None,
                    None,
                    "",
                    date.today().isoformat(),
                    None,
                    False,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    "",
                    get_bookings_table_content(),
                    None,
                    *success_toast("تم حفظ الحجز بنجاح"),
                )
            return (
                True,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
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
                _booking_alert(msg),
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 4. Delete Open
        if ctx_id == "btn-delete-booking" and n_del and active_tab == "tab-bookings":
            return build_booking_manage_default_result(False, True)

        # 5. Confirm Delete
        if ctx_id == "btn-confirm-delete-b" and n_confirm and active_tab == "tab-bookings":
            # Explicit confirmation result messaging:
            # - success alert when deletion succeeds
            # - clear failure/warning alert when deletion fails or nothing selected
            if search_val:
                ok, msg = logic_module.delete_booking(search_val)
                if ok:
                    return (
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        None,
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        "",
                        get_bookings_table_content(),
                        None,
                        *success_toast("\u2705 \u062a\u0645 \u062d\u0630\u0641 \u0627\u0644\u062d\u062c\u0632 \u0628\u0646\u062c\u0627\u062d"),
                    )

                alert = dbc.Alert(
                    f"\u274c \u0644\u0627 \u064a\u0645\u0643\u0646 \u062d\u0630\u0641 \u0627\u0644\u062d\u062c\u0632: {delete_reason(msg)}",
                    color="danger",
                )
                return (
                    False,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
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
                    "",
                    html.Div([alert, get_bookings_table_content()]),
                    no_update,
                    no_update,
                    no_update,
                )

            warning_alert = dbc.Alert(
                "\u26a0\ufe0f \u0627\u062e\u062a\u0631 \u062d\u062c\u0632\u0627\u064b \u0642\u0628\u0644 \u0627\u0644\u062d\u0630\u0641",
                color="warning",
            )
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
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
                "",
                html.Div([warning_alert, get_bookings_table_content()]),
                no_update,
                no_update,
                no_update,
            )


        # 6. Cancel
        if ctx_id == "btn-cancel-delete-b" and n_cancel and active_tab == "tab-bookings":
            return build_booking_manage_default_result(False, False)

        return build_booking_manage_default_result(is_open, is_del_open)

    @app.callback(
        Output("b-status", "value", allow_duplicate=True),
        [Input("btn-add-booking-modal", "n_clicks"), Input("btn-edit-booking", "n_clicks")],
        State("b-search", "value"),
        prevent_initial_call=True,
    )
    def sync_booking_status_field(_n_add, _n_edit, search_val):
        trigger = ctx.triggered_id
        default_status = getattr(logic_module, "BOOKING_STATUS_ACTIVE", "\u0646\u0634\u0637")
        if trigger == "btn-add-booking-modal":
            return default_status
        if trigger == "btn-edit-booking" and search_val:
            df = load_data("bookings.csv", b_cols)
            row = df[df[b_cols[0]] == search_val]
            if row.empty:
                return no_update
            if len(b_cols) > 11 and b_cols[11] in row.columns:
                val = str(row.iloc[0][b_cols[11]] or "").strip()
                return val or default_status
            return default_status
        return no_update

    @app.callback(
        [Output("b-customer", "options", allow_duplicate=True), Output("b-customer", "value", allow_duplicate=True)],
        Input("last-added-customer", "data"),
        State("modal-booking", "is_open"),
        prevent_initial_call=True,
    )
    def refresh_booking_customers_after_quick_add(last_added_customer, is_booking_open):
        # Only refresh booking customers when booking modal is open and a customer was just added.
        if not is_booking_open or not last_added_customer:
            return no_update, no_update

        c_df = load_data("customers.csv", c_cols)
        if c_df.empty:
            return no_update, no_update

        c_opts = build_booking_customer_options(c_df, c_cols)
        if not c_opts:
            return no_update, no_update

        selected = last_added_customer if last_added_customer in {opt["value"] for opt in c_opts} else no_update
        return c_opts, selected

    @app.callback(
        Output("dresses-table-container", "children", allow_duplicate=True),
        Input("bookings-table-container", "children"),
        prevent_initial_call=True,
    )
    def refresh_dresses_on_booking_change(_):
        return get_dresses_table_content()

    @app.callback(
        Output("payments-table-container", "children", allow_duplicate=True),
        Input("bookings-table-container", "children"),
        prevent_initial_call=True,
    )
    def refresh_payments_on_booking_change(_):
        return get_payments_table_content()

    @app.callback(
        [Output("b-dept", "options"), Output("b-dept", "value", allow_duplicate=True)],
        [
            Input("dept-table-container", "children"),
            Input("main-tabs", "active_tab"),
            Input("modal-booking", "is_open"),
        ],
        State("b-dept", "value"),
        prevent_initial_call=True,
    )
    def refresh_booking_department_options(_dept_table, _active_tab, _is_open, current_dept):
        dept_df = logic_module.check_departments() if hasattr(logic_module, "check_departments") else None
        if dept_df is None or dept_df.empty or "department_name" not in dept_df.columns:
            return [], None

        options = []
        seen = set()
        for raw_name in dept_df["department_name"].tolist():
            name = str(raw_name).strip()
            if not name or name in seen:
                continue
            seen.add(name)
            options.append({"label": name, "value": name})

        valid_values = {opt["value"] for opt in options}
        next_value = current_dept if current_dept in valid_values else None
        return options, next_value

    @app.callback(
        [
            Output("b-customer", "options", allow_duplicate=True),
            Output("b-customer", "value", allow_duplicate=True),
        ],
        [
            Input("customers-table-container", "children"),
            Input("main-tabs", "active_tab"),
            Input("last-added-customer", "data"),
            Input("modal-booking", "is_open"),
        ],
        State("b-customer", "value"),
        prevent_initial_call=True,
    )
    def refresh_booking_customer_options(
        _customers_table,
        _active_tab,
        last_added_customer,
        _is_open,
        current_customer,
    ):
        c_df = load_data("customers.csv", c_cols)
        options = build_booking_customer_options(c_df, c_cols)
        valid_values = {opt["value"] for opt in options}
        if current_customer in valid_values:
            next_value = current_customer
        elif last_added_customer in valid_values:
            # Keep quick-added customer selected when options are refreshed.
            next_value = last_added_customer
        else:
            next_value = None
        return options, next_value

    @app.callback(
        [
            Output("b-dress", "options", allow_duplicate=True),
            Output("b-dress", "value", allow_duplicate=True),
        ],
        [
            Input("dresses-table-container", "children"),
            Input("main-tabs", "active_tab"),
            Input("modal-booking", "is_open"),
        ],
        State("b-dress", "value"),
        prevent_initial_call=True,
    )
    def refresh_booking_dress_options(_dresses_table, _active_tab, _is_open, current_dress):
        d_df = load_data("dresses.csv", d_cols)
        options = build_booking_dress_options(d_df, d_cols)
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
        [
            Input("services-table-container", "children"),
            Input("b-dept", "value"),
            Input("modal-booking", "is_open"),
            Input("main-tabs", "active_tab"),
        ],
        State("b-service", "value"),
        prevent_initial_call=True,
    )
    def refresh_booking_service_options(_services_table, dept, _is_open, _active_tab, current_service):
        if not dept:
            return [], None, {"display": "none"}

        s_df = load_data("services.csv", s_cols)
        options = build_booking_service_options_for_dept(s_df, s_cols, dept)
        valid_values = {opt["value"] for opt in options}
        next_value = current_service if current_service in valid_values else None
        d_style = {"display": "block"} if is_dresses_dept(dept) else {"display": "none"}
        return options, next_value, d_style
