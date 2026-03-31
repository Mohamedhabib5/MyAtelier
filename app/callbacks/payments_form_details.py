from dash import Input, Output, State, html, no_update

from app.callbacks.payments_form_helpers import build_booking_details, build_booking_options


def register_payments_form_detail_callbacks(app, load_data, b_cols):
    @app.callback(
        [Output("p-booking", "options", allow_duplicate=True), Output("p-booking", "value", allow_duplicate=True)],
        [Input("bookings_data", "data"), Input("modal-payment", "is_open")],
        State("p-booking", "value"),
        prevent_initial_call=True,
    )
    def refresh_payment_booking_options(bookings_data, is_open, current_booking):
        if not is_open:
            return no_update, no_update
        booking_options, _ = build_booking_options(load_data, b_cols, bookings_data)
        valid_values = {opt["value"] for opt in booking_options}
        return booking_options, current_booking if current_booking in valid_values else None

    @app.callback(
        Output("p-booking-details", "children"),
        [Input("p-booking", "value"), Input("bookings_data", "data"), Input("modal-payment", "is_open")],
    )
    def refresh_payment_booking_details(selected_booking_id, bookings_data, is_modal_open):
        if not is_modal_open:
            return ""
        if not selected_booking_id:
            return html.Div("اختر حجزًا لعرض المتبقي الحالي.")
        return build_booking_details(selected_booking_id, bookings_data, load_data, b_cols)
