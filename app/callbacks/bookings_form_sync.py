from dash import Input, Output, State, ctx, no_update


def register_bookings_form_sync_callbacks(
    app,
    load_data,
    b_cols,
    logic_module,
):
    @app.callback(
        Output("b-status", "value", allow_duplicate=True),
        [Input("btn-add-booking-modal", "n_clicks"), Input("btn-edit-booking", "n_clicks")],
        State("b-search", "value"),
        prevent_initial_call=True,
    )
    def sync_booking_status_field(_n_add, _n_edit, search_val):
        trigger = ctx.triggered_id
        default_status = getattr(logic_module, "BOOKING_STATUS_ACTIVE", "نشط")
        if trigger == "btn-add-booking-modal":
            return default_status
        if trigger == "btn-edit-booking" and search_val:
            df = load_data("bookings.csv", b_cols)
            row = df[df[b_cols[0]] == search_val]
            if row.empty:
                return no_update
            if len(b_cols) > 11 and b_cols[11] in row.columns:
                value = str(row.iloc[0][b_cols[11]] or "").strip()
                return value or default_status
            return default_status
        return no_update
