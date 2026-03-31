from datetime import date

import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, html, no_update

from app.callbacks.feedback import success_toast
from app.callbacks.payments_form_helpers import build_booking_options


def register_payments_form_core_callbacks(
    app,
    load_data,
    b_cols,
    p_cols,
    get_payments_table_content,
    logic_module,
):
    @app.callback(
        [
            Output("modal-payment", "is_open"),
            Output("p-modal-title", "children"),
            Output("p-booking", "value", allow_duplicate=True),
            Output("p-amount", "value"),
            Output("p-notes", "value"),
            Output("p-date", "value"),
            Output("p-edit-id", "data"),
            Output("modal-delete-payment", "is_open"),
            Output("p-booking", "options", allow_duplicate=True),
            Output("p-alert", "children"),
            Output("payments-table-container", "children"),
            Output("p-search", "value", allow_duplicate=True),
            Output("app-success-toast", "children", allow_duplicate=True),
            Output("app-success-toast", "is_open", allow_duplicate=True),
        ],
        [
            Input("btn-add-payment-modal", "n_clicks"),
            Input("btn-edit-payment", "n_clicks"),
            Input("btn-save-payment", "n_clicks"),
            Input("btn-delete-payment", "n_clicks"),
            Input("btn-cancel-delete-p", "n_clicks"),
            Input("btn-confirm-delete-p", "n_clicks"),
        ],
        [
            State("modal-payment", "is_open"),
            State("p-search", "value"),
            State("modal-delete-payment", "is_open"),
            State("main-tabs", "active_tab"),
            State("btn-add-payment-modal", "n_clicks_timestamp"),
            State("btn-edit-payment", "n_clicks_timestamp"),
            State("btn-save-payment", "n_clicks_timestamp"),
            State("btn-delete-payment", "n_clicks_timestamp"),
            State("btn-cancel-delete-p", "n_clicks_timestamp"),
            State("btn-confirm-delete-p", "n_clicks_timestamp"),
            State("user_session_store", "data"),
            State("viewport-mode", "data"),
            State("bookings_data", "data"),
            State("p-booking", "value"),
            State("p-amount", "value"),
            State("p-notes", "value"),
            State("p-date", "value"),
            State("p-edit-id", "data"),
        ],
        prevent_initial_call=True,
    )
    def manage_payments(
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
        viewport_mode,
        bookings_data,
        booking_id,
        amount,
        notes,
        payment_date,
        edit_id,
    ):
        def _out(payload, toast_msg=no_update, toast_open=no_update):
            return (*payload, toast_msg, toast_open)

        triggered_val = None
        if getattr(ctx, "triggered", None):
            triggered_val = ctx.triggered[0].get("value")
        if not isinstance(triggered_val, (int, float)) or triggered_val <= 0:
            return _out((False, no_update, no_update, no_update, no_update, no_update, no_update, False, no_update, no_update, no_update, no_update))

        ctx_id = ctx.triggered_id
        login_ts = 0
        if isinstance(session_data, dict):
            try:
                login_ts = float(session_data.get("login_ts") or 0)
            except Exception:
                login_ts = 0
        ts_map = {
            "btn-add-payment-modal": add_ts,
            "btn-edit-payment": edit_ts,
            "btn-save-payment": save_ts,
            "btn-delete-payment": del_ts,
            "btn-cancel-delete-p": cancel_ts,
            "btn-confirm-delete-p": confirm_ts,
        }
        try:
            trigger_ts = float(ts_map.get(ctx_id) or 0)
        except Exception:
            trigger_ts = 0
        if ctx_id in ts_map and login_ts > 0 and trigger_ts > 0 and trigger_ts < login_ts:
            return _out((False, no_update, no_update, no_update, no_update, no_update, no_update, False, no_update, no_update, no_update, no_update))

        booking_options, _ = build_booking_options(load_data, b_cols, bookings_data)

        if ctx_id == "btn-add-payment-modal" and n_add and active_tab == "tab-payments":
            return _out((True, "تسجيل دفعة جديدة", None, None, "", date.today().isoformat(), None, False, booking_options, "", no_update, no_update))

        if ctx_id == "btn-edit-payment" and n_edit and active_tab == "tab-payments" and search_val:
            df = load_data("payments.csv", p_cols)
            row = df[df["كود الدفع"] == search_val]
            if not row.empty:
                record = row.iloc[0]
                if "نوع الدفعة" in row.columns and str(record.get("نوع الدفعة", "booking_installment")) != "booking_installment":
                    return _out((
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        False,
                        booking_options,
                        dbc.Alert("لا يمكن تعديل دفعات التعويض أو التأمين من هذه الشاشة.", color="warning"),
                        no_update,
                        no_update,
                    ))
                return _out((
                    True,
                    "تعديل دفعة: " + str(record["كود الدفع"]),
                    record["كود الحجز"],
                    record["القيمة المدفوعة"],
                    record["ملاحظات الدفع"],
                    record["التاريخ"],
                    search_val,
                    False,
                    booking_options,
                    "",
                    no_update,
                    no_update,
                ))

        if ctx_id == "btn-save-payment" and n_save and active_tab == "tab-payments":
            if not booking_id or not amount:
                return _out((
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    no_update,
                    dbc.Alert("⚠️ اختر الحجز والمبلغ", color="warning"),
                    no_update,
                    no_update,
                ))
            if edit_id:
                success, msg = logic_module.update_payment(edit_id, booking_id, amount, notes, payment_date)
                if success:
                    return _out((
                        False,
                        no_update,
                        None,
                        None,
                        "",
                        date.today().isoformat(),
                        None,
                        False,
                        booking_options,
                        "",
                        get_payments_table_content(viewport_mode=viewport_mode),
                        None,
                    ), *success_toast("تم تعديل الدفعة بنجاح"))
                return _out((
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    no_update,
                    dbc.Alert(f"❌ {msg}", color="danger"),
                    no_update,
                    no_update,
                ))

            success, msg = logic_module.add_payment(booking_id, amount, "", "", notes, payment_date)
            if success:
                return _out((
                    False,
                    no_update,
                    None,
                    None,
                    "",
                    date.today().isoformat(),
                    None,
                    False,
                    booking_options,
                    "",
                    get_payments_table_content(viewport_mode=viewport_mode),
                    None,
                ), *success_toast("تم حفظ الدفعة بنجاح"))
            return _out((
                True,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                no_update,
                dbc.Alert(f"❌ {msg}", color="danger"),
                no_update,
                no_update,
            ))

        if ctx_id == "btn-delete-payment" and n_del and active_tab == "tab-payments":
            return _out((False, no_update, no_update, no_update, no_update, no_update, no_update, True, no_update, "", no_update, no_update))

        if ctx_id == "btn-confirm-delete-p" and n_confirm and active_tab == "tab-payments":
            if search_val:
                df = load_data("payments.csv", p_cols)
                row = df[df["كود الدفع"] == search_val]
                if not row.empty:
                    record = row.iloc[0]
                    if "نوع الدفعة" in row.columns and str(record.get("نوع الدفعة", "booking_installment")) != "booking_installment":
                        warning_alert = dbc.Alert("لا يمكن حذف دفعات التعويض أو التأمين من شاشة الدفعات العامة.", color="warning")
                        return _out((
                            False,
                            no_update,
                            no_update,
                            no_update,
                            no_update,
                            no_update,
                            no_update,
                            False,
                            no_update,
                            "",
                            html.Div([warning_alert, get_payments_table_content(viewport_mode=viewport_mode)]),
                            no_update,
                        ))
                if logic_module.delete_payment(search_val):
                    return _out((
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        False,
                        no_update,
                        "",
                        get_payments_table_content(viewport_mode=viewport_mode),
                        None,
                    ), *success_toast("تم حذف الدفعة بنجاح"))
                danger_alert = dbc.Alert("❌ تعذر حذف الدفعة", color="danger")
                return _out((
                    False,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    no_update,
                    "",
                    html.Div([danger_alert, get_payments_table_content(viewport_mode=viewport_mode)]),
                    no_update,
                ))
            warning_alert = dbc.Alert("⚠️ اختر دفعة قبل الحذف", color="warning")
            return _out((
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                no_update,
                "",
                html.Div([warning_alert, get_payments_table_content(viewport_mode=viewport_mode)]),
                no_update,
            ))

        if ctx_id == "btn-cancel-delete-p" and n_cancel and active_tab == "tab-payments":
            return _out((False, no_update, no_update, no_update, no_update, no_update, no_update, False, no_update, "", no_update, no_update))

        return _out((is_open, no_update, no_update, no_update, no_update, no_update, no_update, is_del_open, no_update, no_update, no_update, no_update))
