from datetime import date

import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, html, no_update
from app.callbacks.feedback import success_toast


def register_dresses_form_callbacks(
    app,
    load_data,
    d_cols,
    get_dresses_table_content,
    logic_module,
    delete_reason,
):
    @app.callback(
        [
            Output("modal-dress", "is_open"),
            Output("d-modal-title", "children"),
            Output("d-code", "value"),
            Output("d-type", "value"),
            Output("d-date", "value"),
            Output("d-status", "value"),
            Output("d-desc", "value"),
            Output("d-upload-output", "children"),
            Output("d-edit-id", "data"),
            Output("modal-delete-dress", "is_open"),
            Output("d-alert", "children"),
            Output("dresses-table-container", "children"),
            Output("d-search", "value", allow_duplicate=True),
            Output("app-success-toast", "children", allow_duplicate=True),
            Output("app-success-toast", "is_open", allow_duplicate=True),
        ],
        [
            Input("btn-add-dress-modal", "n_clicks"),
            Input("btn-edit-dress", "n_clicks"),
            Input("btn-save-dress", "n_clicks"),
            Input("btn-delete-dress", "n_clicks"),
            Input("btn-cancel-delete-d", "n_clicks"),
            Input("btn-confirm-delete-d", "n_clicks"),
            Input("d-upload-image", "contents"),
        ],
        [
            State("modal-dress", "is_open"),
            State("d-search", "value"),
            State("modal-delete-dress", "is_open"),
            State("main-tabs", "active_tab"),
            State("btn-add-dress-modal", "n_clicks_timestamp"),
            State("btn-edit-dress", "n_clicks_timestamp"),
            State("btn-save-dress", "n_clicks_timestamp"),
            State("btn-delete-dress", "n_clicks_timestamp"),
            State("btn-cancel-delete-d", "n_clicks_timestamp"),
            State("btn-confirm-delete-d", "n_clicks_timestamp"),
            State("user_session_store", "data"),
            State("d-code", "value"),
            State("d-type", "value"),
            State("d-date", "value"),
            State("d-status", "value"),
            State("d-desc", "value"),
            State("d-edit-id", "data"),
            State("d-upload-image", "filename"),
        ],
        prevent_initial_call=True,
    )
    def manage_dresses(
        n_add,
        n_edit,
        n_save,
        n_del,
        n_cancel,
        n_confirm,
        upload_contents,
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
        code,
        dtype,
        buy_date,
        status,
        desc,
        edit_id,
        upload_filename,
    ):
        def ret(*vals):
            if len(vals) == 13:
                return (*vals, no_update, no_update)
            if len(vals) == 15:
                return vals
            raise ValueError(f"Unexpected callback return length: {len(vals)}")

        ctx_id = ctx.triggered_id

        # 0. Upload feedback
        if ctx_id == "d-upload-image" and upload_filename:
            is_image = isinstance(upload_contents, str) and upload_contents.startswith("data:image/")
            if is_image:
                upload_msg = html.Div(
                    [
                        html.Div(f"تم تحديد: {upload_filename}", className="mb-1"),
                        html.Img(
                            src=upload_contents,
                            style={
                                "maxWidth": "220px",
                                "maxHeight": "220px",
                                "borderRadius": "8px",
                                "objectFit": "cover",
                            },
                        ),
                    ]
                )
            else:
                upload_msg = f"تم تحديد: {upload_filename}"
            return ret(
                True,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                upload_msg,
                no_update,
                False,
                "",
                no_update,
                no_update,
            )

        triggered_val = None
        if getattr(ctx, "triggered", None):
            triggered_val = ctx.triggered[0].get("value")
        if not isinstance(triggered_val, (int, float)) or triggered_val <= 0:
            return ret(
                False,
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
            )

        login_ts = 0
        if isinstance(session_data, dict):
            try:
                login_ts = float(session_data.get("login_ts") or 0)
            except Exception:
                login_ts = 0
        ts_map = {
            "btn-add-dress-modal": add_ts,
            "btn-edit-dress": edit_ts,
            "btn-save-dress": save_ts,
            "btn-delete-dress": del_ts,
            "btn-cancel-delete-d": cancel_ts,
            "btn-confirm-delete-d": confirm_ts,
        }
        try:
            trigger_ts = float(ts_map.get(ctx_id) or 0)
        except Exception:
            trigger_ts = 0
        if ctx_id in ts_map and login_ts > 0 and trigger_ts > 0 and trigger_ts < login_ts:
            return ret(
                False,
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
            )

        # 1. Add
        if ctx_id == "btn-add-dress-modal" and n_add and active_tab == "tab-dresses":
            return ret(
                True,
                "إضافة فستان جديد",
                "",
                "زفاف",
                date.today().isoformat(),
                "متاح",
                "",
                "",
                None,
                False,
                "",
                no_update,
                no_update,
            )

        # 2. Edit
        if ctx_id == "btn-edit-dress" and n_edit and active_tab == "tab-dresses" and search_val:
            df = load_data("dresses.csv", d_cols)
            row = df[df["كود الفستان"] == search_val]
            if not row.empty:
                r = row.iloc[0]
                current_img = r.get("صورة الفستان", "")
                img_msg = f"الصورة الحالية: {current_img}" if current_img else "لا توجد صورة"
                return ret(
                    True,
                    f"تعديل فستان: {r['كود الفستان']}",
                    r["كود الفستان"],
                    r["نوع الفستان"],
                    r["تاريخ الشراء"],
                    r["حالة الفستان"],
                    r["وصف الفستان"],
                    img_msg,
                    search_val,
                    False,
                    "",
                    no_update,
                    no_update,
                )

        # 3. Save
        if ctx_id == "btn-save-dress" and n_save and active_tab == "tab-dresses":
            if not code or not desc:
                return ret(
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    dbc.Alert("⚠️ الكود والوصف مطلوبان", color="warning"),
                    no_update,
                    no_update,
                )

            if edit_id:
                success, msg = logic_module.update_dress(
                    edit_id, code, dtype, buy_date, status, desc, upload_contents
                )
                if success:
                    return ret(
                        False,
                        no_update,
                        "",
                        "زفاف",
                        date.today().isoformat(),
                        "متاح",
                        "",
                        "",
                        None,
                        False,
                        "",
                        get_dresses_table_content(),
                        None,
                        *success_toast(f"\u2705 {msg}"),
                    )
                return ret(
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    dbc.Alert(f"❌ {msg}", color="danger"),
                    no_update,
                    no_update,
                )

            success, msg = logic_module.add_dress(
                code, dtype, buy_date, status, desc, upload_contents
            )
            if success:
                return ret(
                    False,
                    no_update,
                    "",
                    "زفاف",
                    date.today().isoformat(),
                    "متاح",
                    "",
                    "",
                    None,
                    False,
                    "",
                    get_dresses_table_content(),
                    None,
                    *success_toast(f"\u2705 {msg}"),
                )
            return ret(
                True,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                dbc.Alert(f"❌ {msg}", color="danger"),
                no_update,
                no_update,
            )

        # 4. Delete open
        if ctx_id == "btn-delete-dress" and n_del and active_tab == "tab-dresses":
            return ret(
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                True,
                "",
                no_update,
                no_update,
            )

        # 5. Confirm delete
        if ctx_id == "btn-confirm-delete-d" and n_confirm and active_tab == "tab-dresses":
            if search_val:
                ok, msg = logic_module.delete_dress(search_val)
                if ok:
                    return ret(
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        False,
                        "",
                        get_dresses_table_content(),
                        None,
                        *success_toast("\u2705 تم حذف الفستان بنجاح"),
                    )
                alert = dbc.Alert(
                    f"❌ لا يمكن حذف الفستان: {delete_reason(msg)}",
                    color="danger",
                )
                return ret(
                    False,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    "",
                    html.Div([alert, get_dresses_table_content()]),
                    no_update,
                )
            warning_alert = dbc.Alert("⚠️ اختر فستانًا قبل الحذف", color="warning")
            return ret(
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                "",
                html.Div([warning_alert, get_dresses_table_content()]),
                no_update,
            )

        # 6. Cancel
        if ctx_id == "btn-cancel-delete-d" and n_cancel and active_tab == "tab-dresses":
            return ret(
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                "",
                no_update,
                no_update,
            )

        return ret(
            is_open,
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
        )
