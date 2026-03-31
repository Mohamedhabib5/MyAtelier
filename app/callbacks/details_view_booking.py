import dash_bootstrap_components as dbc
from dash import html

from app.callbacks.details_view_helpers import float_value, map_lookup


def build_booking_view(booking_id, bookings_by_id, b_cols):
    """Build details modal content for a single booking from stores."""
    row = map_lookup(bookings_by_id, booking_id)

    if not row:
        content = dbc.Alert("لم يتم العثور على الحجز", color="danger")
    else:
        customer_col = b_cols[2] if len(b_cols) > 2 else None
        dept_col = b_cols[3] if len(b_cols) > 3 else None
        service_col = b_cols[4] if len(b_cols) > 4 else None
        event_date_col = b_cols[6] if len(b_cols) > 6 else None
        price_col = b_cols[7] if len(b_cols) > 7 else None
        paid_col = b_cols[8] if len(b_cols) > 8 else None
        remaining_col = b_cols[9] if len(b_cols) > 9 else None
        notes_col = b_cols[10] if len(b_cols) > 10 else None

        content = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col([html.Strong("العروسه: "), html.Span(row.get(customer_col, ""))], width=6),
                        dbc.Col([html.Strong("القسم: "), html.Span(row.get(dept_col, ""))], width=6),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Col([html.Strong("الخدمة: "), html.Span(row.get(service_col, ""))], width=6),
                        dbc.Col([html.Strong("تاريخ المناسبة: "), html.Span(row.get(event_date_col, ""))], width=6),
                    ],
                    className="mb-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Strong("السعر المتفق: "),
                                html.Span(f"{row.get(price_col, 0)} ج", style={"fontSize": "1.1em"}),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Strong("المدفوع: "),
                                html.Span(
                                    f"{row.get(paid_col, 0)} ج",
                                    style={"fontSize": "1.1em", "color": "green"},
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Strong("المتبقي: "),
                                html.Span(
                                    f"{row.get(remaining_col, 0)} ج",
                                    style={
                                        "fontSize": "1.2em",
                                        "fontWeight": "bold",
                                        "color": "red" if float_value(row.get(remaining_col, 0)) > 0 else "green",
                                    },
                                ),
                            ],
                            width=4,
                        ),
                    ],
                    className="mb-3",
                ),
                html.Hr(),
                html.Div(
                    [
                        html.Strong("ملاحظات: "),
                        html.P(row.get(notes_col) or "لا توجد ملاحظات", className="text-muted"),
                    ]
                ),
            ]
        )

    return True, f"تفاصيل الحجز: {booking_id}", content
