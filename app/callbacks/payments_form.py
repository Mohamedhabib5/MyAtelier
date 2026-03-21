from datetime import date

import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, html, no_update
from app.callbacks.feedback import success_toast


def register_payments_form_callbacks(
    app,
    load_data,
    b_cols,
    p_cols,
    get_payments_table_content,
    logic_module,
):
    def _fmt_money(v):
        try:
            return f"{float(v):,.2f}"
        except Exception:
            return str(v or "0")

    def _build_booking_options():
        b_df = load_data("bookings.csv", b_cols)
        if b_df.empty:
            return [], b_df

        booking_id_col = b_cols[0]
        customer_col = b_cols[2] if len(b_cols) > 2 else booking_id_col
        service_col = b_cols[4] if len(b_cols) > 4 else booking_id_col
        remaining_col = b_cols[9] if len(b_cols) > 9 else None

        options = []
        for _, r in b_df.iterrows():
            customer_name = str(r.get(customer_col, "")).strip()
            service_name = str(r.get(service_col, "")).strip()
            if remaining_col is not None:
                remaining_val = _fmt_money(r.get(remaining_col, 0))
                label = f"{customer_name} ({service_name}) - المتبقي: {remaining_val}"
            else:
                label = f"{customer_name} ({service_name})"
            options.append({"label": label, "value": r[booking_id_col]})
        return options, b_df

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
        bid,
        amount,
        notes,
        p_date,
        edit_id,
    ):
        def _out(payload, toast_msg=no_update, toast_open=no_update):
            return (*payload, toast_msg, toast_open)

        triggered_val = None
        if getattr(ctx, "triggered", None):
            triggered_val = ctx.triggered[0].get("value")
        if not isinstance(triggered_val, (int, float)) or triggered_val <= 0:
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
                no_update,
                no_update,
                no_update,
            ))

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
                no_update,
                no_update,
                no_update,
            ))
        b_opts, _ = _build_booking_options()

        # 1. Add
        if ctx_id == "btn-add-payment-modal" and n_add and active_tab == "tab-payments":
            return _out((
                True,
                "\u062a\u0633\u062c\u064a\u0644 \u062f\u0641\u0639\u0629 \u062c\u062f\u064a\u062f\u0629",
                None,
                None,
                "",
                date.today().isoformat(),
                None,
                False,
                b_opts,
                "",
                no_update,
                no_update,
            ))

        # 2. Edit
        if ctx_id == "btn-edit-payment" and n_edit and active_tab == "tab-payments" and search_val:
            df = load_data("payments.csv", p_cols)
            row = df[df["\u0643\u0648\u062f \u0627\u0644\u062f\u0641\u0639"] == search_val]
            if not row.empty:
                r = row.iloc[0]
                return _out((
                    True,
                    "\u062a\u0639\u062f\u064a\u0644 \u062f\u0641\u0639\u0629: "
                    + str(r["\u0643\u0648\u062f \u0627\u0644\u062f\u0641\u0639"]),
                    r["\u0643\u0648\u062f \u0627\u0644\u062d\u062c\u0632"],
                    r["\u0627\u0644\u0642\u064a\u0645\u0629 \u0627\u0644\u0645\u062f\u0641\u0648\u0639\u0629"],
                    r["\u0645\u0644\u0627\u062d\u0638\u0627\u062a \u0627\u0644\u062f\u0641\u0639"],
                    r["\u0627\u0644\u062a\u0627\u0631\u064a\u062e"],
                    search_val,
                    False,
                    b_opts,
                    "",
                    no_update,
                    no_update,
                ))

        # 3. Save
        if ctx_id == "btn-save-payment" and n_save and active_tab == "tab-payments":
            if not bid or not amount:
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
                    dbc.Alert(
                        "\u26a0\ufe0f \u0627\u062e\u062a\u0631 \u0627\u0644\u062d\u062c\u0632 \u0648\u0627\u0644\u0645\u0628\u0644\u063a",
                        color="warning",
                    ),
                    no_update,
                    no_update,
                ))

            if edit_id:  # Edit
                success, msg = logic_module.update_payment(edit_id, bid, amount, notes, p_date)
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
                        b_opts,
                        "",
                        get_payments_table_content(),
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
                    dbc.Alert(f"\u274c {msg}", color="danger"),
                    no_update,
                    no_update,
                ))

            # Add
            success, msg = logic_module.add_payment(bid, amount, "", "", notes, p_date)
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
                    b_opts,
                    "",
                    get_payments_table_content(),
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
                dbc.Alert(f"\u274c {msg}", color="danger"),
                no_update,
                no_update,
            ))

        # 4. Delete Open
        if ctx_id == "btn-delete-payment" and n_del and active_tab == "tab-payments":
            return _out((
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                True,
                no_update,
                "",
                no_update,
                no_update,
            ))

        # 5. Confirm Delete
        if ctx_id == "btn-confirm-delete-p" and n_confirm and active_tab == "tab-payments":
            if search_val:
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
                        get_payments_table_content(),
                        None,
                    ), *success_toast("تم حذف الدفعة بنجاح"))
                danger_alert = dbc.Alert(
                    "❌ تعذر حذف الدفعة",
                    color="danger",
                )
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
                    html.Div([danger_alert, get_payments_table_content()]),
                    no_update,
                ))
            warning_alert = dbc.Alert(
                "⚠️ اختر دفعة قبل الحذف",
                color="warning",
            )
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
                html.Div([warning_alert, get_payments_table_content()]),
                no_update,
            ))

        # 6. Cancel
        if ctx_id == "btn-cancel-delete-p" and n_cancel and active_tab == "tab-payments":
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
                no_update,
                no_update,
            ))

        return _out((
            is_open,
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
        ))

    @app.callback(
        [
            Output("p-booking", "options", allow_duplicate=True),
            Output("p-booking", "value", allow_duplicate=True),
        ],
        [
            Input("bookings-table-container", "children"),
            Input("customers-table-container", "children"),
            Input("services-table-container", "children"),
            Input("main-tabs", "active_tab"),
            Input("modal-payment", "is_open"),
        ],
        State("p-booking", "value"),
        prevent_initial_call=True,
    )
    def refresh_payment_booking_options(
        _bookings_table,
        _customers_table,
        _services_table,
        _active_tab,
        _is_open,
        current_booking,
    ):
        b_opts, _ = _build_booking_options()

        valid_values = {opt["value"] for opt in b_opts}
        next_value = current_booking if current_booking in valid_values else None
        return b_opts, next_value

    @app.callback(
        Output("p-booking-details", "children"),
        [
            Input("p-booking", "value"),
            Input("bookings-table-container", "children"),
            Input("modal-payment", "is_open"),
        ],
    )
    def refresh_payment_booking_details(selected_booking_id, _bookings_table, is_modal_open):
        if not is_modal_open:
            return ""
        if not selected_booking_id:
            return html.Div("اختر حجزًا لعرض المتبقي الحالي.")

        _, b_df = _build_booking_options()
        if b_df.empty:
            return dbc.Alert("لا توجد بيانات حجز متاحة.", color="warning")

        booking_id_col = b_cols[0]
        customer_col = b_cols[2] if len(b_cols) > 2 else booking_id_col
        service_col = b_cols[4] if len(b_cols) > 4 else booking_id_col
        price_col = b_cols[7] if len(b_cols) > 7 else None
        paid_col = b_cols[8] if len(b_cols) > 8 else None
        remaining_col = b_cols[9] if len(b_cols) > 9 else None

        row = b_df[b_df[booking_id_col] == selected_booking_id]
        if row.empty:
            return dbc.Alert("تعذر تحميل تفاصيل الحجز.", color="warning")

        r = row.iloc[0]
        details = [
            html.Div(f"كود الحجز: {r.get(booking_id_col, '-')}", className="fw-bold"),
            html.Div(f"العروسة: {r.get(customer_col, '-')}"),
            html.Div(f"الخدمة: {r.get(service_col, '-')}"),
        ]
        if price_col:
            details.append(html.Div(f"السعر المتفق: {_fmt_money(r.get(price_col, 0))}"))
        if paid_col:
            details.append(html.Div(f"المدفوع: {_fmt_money(r.get(paid_col, 0))}"))
        if remaining_col:
            details.append(html.Div(f"المتبقي الحالي: {_fmt_money(r.get(remaining_col, 0))}", className="fw-bold"))
        return html.Div(details)
