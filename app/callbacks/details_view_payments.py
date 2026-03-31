import dash_bootstrap_components as dbc
from dash import html

from app.callbacks.details_view_helpers import float_value, map_lookup, rows, same_value


def build_payments_view(
    booking_id,
    payments_records,
    bookings_by_id,
    p_cols,
    b_cols,
    payments_records_loader=None,
):
    """Build details modal content for booking payments from stores."""
    booking_id_col = p_cols[2] if len(p_cols) > 2 else None
    payment_rows = rows(payments_records)
    filtered = [
        row for row in payment_rows
        if booking_id_col and same_value(row.get(booking_id_col), booking_id)
    ]
    if not filtered and not payment_rows and callable(payments_records_loader):
        loaded_rows = payments_records_loader() or []
        if isinstance(loaded_rows, list):
            payment_rows = loaded_rows
            filtered = [
                row for row in payment_rows
                if booking_id_col and same_value(row.get(booking_id_col), booking_id)
            ]

    if not filtered:
        content = dbc.Alert("لا توجد مدفوعات لهذا الحجز", color="warning")
    else:
        booking = map_lookup(bookings_by_id, booking_id) or {}
        remaining_col = b_cols[9] if len(b_cols) > 9 else None
        remaining = booking.get(remaining_col, "غير معروف") if remaining_col else "غير معروف"

        payment_id_col = p_cols[0] if len(p_cols) > 0 else None
        payment_date_col = p_cols[1] if len(p_cols) > 1 else None
        amount_col = p_cols[3] if len(p_cols) > 3 else None
        notes_col = p_cols[7] if len(p_cols) > 7 else None

        table = dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("كود الدفع"),
                            html.Th("المبلغ"),
                            html.Th("التاريخ"),
                            html.Th("ملاحظات"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(row.get(payment_id_col, "")),
                                html.Td(
                                    f"{row.get(amount_col, 0)} ج",
                                    style={"fontWeight": "bold", "color": "green"},
                                ),
                                html.Td(row.get(payment_date_col, "")),
                                html.Td(row.get(notes_col, "")),
                            ]
                        )
                        for row in filtered
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            striped=True,
            className="table-sm",
        )

        content = html.Div(
            [
                dbc.Alert(
                    [
                        html.Strong("المبلغ المتبقي: "),
                        html.Span(
                            f"{remaining} ج",
                            style={
                                "fontSize": "1.2em",
                                "color": "red" if float_value(remaining) > 0 else "green",
                            },
                        ),
                    ],
                    color="info",
                    className="mb-3",
                ),
                table,
                html.Hr(),
                html.P(
                    [
                        html.Strong("إجمالي المدفوعات: "),
                        f"{sum(float_value(row.get(amount_col, 0)) for row in filtered)} ج",
                    ],
                    className="text-end",
                ),
            ]
        )

    return f"مدفوعات الحجز: {booking_id}", content
