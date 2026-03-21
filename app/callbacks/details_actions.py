from dash import ALL, Input, Output, ctx, no_update

from app.callbacks.details_view import (
    build_booking_view,
    build_customer_bookings_view,
    build_dress_bookings_view,
    build_payments_view,
)


def register_details_actions_callback(
    app,
    load_data,
    c_cols,
    b_cols,
    p_cols,
    normalize_code,
    payments_action_label,
    customer_bookings_action_label,
    dress_bookings_action_label,
    payment_booking_action_label,
):
    @app.callback(
        [
            Output("modal-details-viewer", "is_open"),
            Output("details-viewer-title", "children"),
            Output("details-viewer-body", "children"),
        ],
        [
            Input({"type": "view-payments", "index": ALL}, "n_clicks"),
            Input({"type": "view-customer-bookings", "index": ALL}, "n_clicks"),
            Input({"type": "view-booking", "index": ALL}, "n_clicks"),
            Input({"type": "view-dress-bookings", "index": ALL}, "n_clicks"),
            Input({"type": "grid", "index": ALL}, "cellClicked"),
            Input("dresses-table", "cellClicked"),
            Input("btn-close-details", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def handle_view_details(
        _view_payments_clicks,
        _view_customer_clicks,
        _view_booking_clicks,
        _view_dress_clicks,
        _grid_cell_clicked,
        dress_cell_clicked,
        _close_clicks,
    ):
        ctx_id = ctx.triggered_id
        triggered_cell_clicked = ctx.triggered[0]["value"] if ctx.triggered else None

        if ctx_id == "btn-close-details":
            return False, "", ""

        def _build_payments(booking_id):
            return build_payments_view(booking_id, load_data=load_data, p_cols=p_cols, b_cols=b_cols)

        def _build_customer_bookings(customer_name):
            return build_customer_bookings_view(customer_name, load_data=load_data, b_cols=b_cols)

        def _build_dress_bookings(dress_code):
            return build_dress_bookings_view(
                dress_code,
                load_data=load_data,
                b_cols=b_cols,
                normalize_code=normalize_code,
            )

        def _build_booking(booking_id):
            return build_booking_view(booking_id, load_data=load_data, b_cols=b_cols)

        def _is_action_click(cell_clicked, label, action_col_ids):
            if not cell_clicked:
                return False
            col_id = cell_clicked.get("colId") or cell_clicked.get("columnId")
            col_def = cell_clicked.get("colDef") or {}
            field = cell_clicked.get("field") or col_def.get("field")
            value = cell_clicked.get("value")
            value_formatted = cell_clicked.get("valueFormatted")
            displayed_value = cell_clicked.get("displayedValue")
            cell_class = col_def.get("cellClass")

            value_str = str(value).strip() if value is not None else ""
            value_formatted_str = str(value_formatted).strip() if value_formatted is not None else ""
            displayed_value_str = str(displayed_value).strip() if displayed_value is not None else ""

            return (
                col_id in action_col_ids
                or field == "__action__"
                or value_str == label
                or value_formatted_str == label
                or displayed_value_str == label
                or cell_class == "ag-action-cell"
                or (isinstance(cell_class, (list, tuple)) and "ag-action-cell" in cell_class)
            )

        def _handle_bookings_grid_click():
            if not (isinstance(ctx_id, dict) and ctx_id.get("type") == "grid" and ctx_id.get("index") == "bookings-table"):
                return None
            if not _is_action_click(triggered_cell_clicked, payments_action_label, {"view-payments-action", "__action__"}):
                return no_update, no_update, no_update

            row_id = triggered_cell_clicked.get("rowId") if triggered_cell_clicked else None
            data = triggered_cell_clicked.get("data") if triggered_cell_clicked else {}
            booking_id_col = b_cols[0] if len(b_cols) > 0 else None
            booking_id = row_id or (data.get(booking_id_col) if booking_id_col and isinstance(data, dict) else None)
            if booking_id:
                title, content = _build_payments(booking_id)
                return True, title, content
            return no_update, no_update, no_update

        def _handle_customers_grid_click():
            if not (isinstance(ctx_id, dict) and ctx_id.get("type") == "grid" and ctx_id.get("index") == "customers-table"):
                return None
            if not _is_action_click(triggered_cell_clicked, customer_bookings_action_label, {"view-customer-bookings-action", "__action__"}):
                return no_update, no_update, no_update

            row_id = triggered_cell_clicked.get("rowId") if triggered_cell_clicked else None
            data = triggered_cell_clicked.get("data") if triggered_cell_clicked else {}
            customer_id_col = c_cols[0] if len(c_cols) > 0 else None
            customer_name_col = c_cols[2] if len(c_cols) > 2 else None

            customer_name = None
            if row_id and customer_id_col and customer_name_col:
                c_df = load_data("customers.csv", c_cols)
                if customer_id_col in c_df.columns and customer_name_col in c_df.columns:
                    match = c_df[c_df[customer_id_col].astype(str) == str(row_id)]
                    if not match.empty:
                        customer_name = match.iloc[0][customer_name_col]

            if not customer_name and isinstance(data, dict) and customer_name_col:
                customer_name = data.get(customer_name_col)

            if isinstance(customer_name, str):
                customer_name = customer_name.strip()
            if customer_name:
                return _build_customer_bookings(customer_name)
            return no_update, no_update, no_update

        def _handle_payments_grid_click():
            if not (isinstance(ctx_id, dict) and ctx_id.get("type") == "grid" and ctx_id.get("index") == "payments-table"):
                return None
            if not _is_action_click(triggered_cell_clicked, payment_booking_action_label, {"view-booking-action", "__action__"}):
                return no_update, no_update, no_update

            row_id = triggered_cell_clicked.get("rowId") if triggered_cell_clicked else None
            data = triggered_cell_clicked.get("data") if triggered_cell_clicked else {}
            payment_id_col = p_cols[0] if len(p_cols) > 0 else None
            booking_id_col = p_cols[2] if len(p_cols) > 2 else None

            booking_id = None
            if row_id and payment_id_col and booking_id_col:
                p_df = load_data("payments.csv", p_cols)
                if payment_id_col in p_df.columns and booking_id_col in p_df.columns:
                    match = p_df[p_df[payment_id_col].astype(str) == str(row_id)]
                    if not match.empty:
                        booking_id = match.iloc[0][booking_id_col]

            if not booking_id and isinstance(data, dict) and booking_id_col:
                booking_id = data.get(booking_id_col)

            if booking_id:
                return _build_booking(booking_id)
            return no_update, no_update, no_update

        def _handle_dresses_grid_click():
            if ctx_id != "dresses-table":
                return None
            if not dress_cell_clicked:
                return no_update, no_update, no_update

            data = dress_cell_clicked.get("data") or {}
            data_action = data.get("__action__") if isinstance(data, dict) else ""
            if not _is_action_click(dress_cell_clicked, dress_bookings_action_label, {"view-dress-bookings-action", "__action__"}) and data_action != dress_bookings_action_label:
                return no_update, no_update, no_update

            row_id = dress_cell_clicked.get("rowId")
            dress_code = row_id
            if not dress_code and isinstance(data, dict):
                dress_code = (
                    data.get("dress_code")
                    or data.get("code")
                    or data.get("\u0643\u0648\u062f \u0627\u0644\u0641\u0633\u062a\u0627\u0646")
                )
            if isinstance(dress_code, str):
                dress_code = dress_code.strip()
            if dress_code:
                return _build_dress_bookings(dress_code)
            return no_update, no_update, no_update

        for grid_handler in (
            _handle_bookings_grid_click,
            _handle_customers_grid_click,
            _handle_payments_grid_click,
            _handle_dresses_grid_click,
        ):
            grid_result = grid_handler()
            if grid_result is not None:
                return grid_result

        if isinstance(ctx_id, dict):
            trigger_type = ctx_id.get("type")
            trigger_index = ctx_id.get("index")
            if trigger_type == "view-payments":
                title, content = _build_payments(trigger_index)
                return True, title, content
            if trigger_type == "view-customer-bookings":
                return _build_customer_bookings(trigger_index)
            if trigger_type == "view-booking":
                return _build_booking(trigger_index)
            if trigger_type == "view-dress-bookings":
                return _build_dress_bookings(trigger_index)

        return no_update, no_update, no_update
