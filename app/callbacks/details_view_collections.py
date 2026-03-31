import dash_bootstrap_components as dbc
from dash import html

from app.callbacks.details_view_helpers import float_value, rows, same_value


def build_customer_bookings_view(customer_name, bookings_records, b_cols):
    """Build details modal content for customer bookings from stores."""
    customer_col = b_cols[2] if len(b_cols) > 2 else None
    filtered = [
        row for row in rows(bookings_records)
        if customer_col and same_value(row.get(customer_col), customer_name)
    ]

    if not filtered:
        content = dbc.Alert("لا توجد حجوزات لهذه العروسة", color="warning")
    else:
        booking_id_col = b_cols[0] if len(b_cols) > 0 else None
        dept_col = b_cols[3] if len(b_cols) > 3 else None
        service_col = b_cols[4] if len(b_cols) > 4 else None
        event_date_col = b_cols[6] if len(b_cols) > 6 else None
        price_col = b_cols[7] if len(b_cols) > 7 else None
        remaining_col = b_cols[9] if len(b_cols) > 9 else None
        total_remaining = sum(float_value(row.get(remaining_col, 0)) for row in filtered) if remaining_col else 0.0

        table = dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("كود الحجز"),
                            html.Th("القسم"),
                            html.Th("الخدمة"),
                            html.Th("تاريخ المناسبة"),
                            html.Th("السعر"),
                            html.Th("المتبقي"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(row.get(booking_id_col, "")),
                                html.Td(row.get(dept_col, "")),
                                html.Td(row.get(service_col, "")),
                                html.Td(row.get(event_date_col, "")),
                                html.Td(f"{row.get(price_col, 0)} ج"),
                                html.Td(
                                    f"{row.get(remaining_col, 0)} ج",
                                    style={
                                        "fontWeight": "bold",
                                        "color": "red" if float_value(row.get(remaining_col, 0)) > 0 else "green",
                                    },
                                ),
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
                table,
                html.Hr(),
                dbc.Alert(
                    [
                        html.Strong("إجمالي المتبقي: "),
                        html.Span(
                            f"{total_remaining} ج",
                            style={
                                "fontSize": "1.2em",
                                "fontWeight": "bold",
                                "color": "red" if total_remaining > 0 else "green",
                            },
                        ),
                    ],
                    color="warning" if total_remaining > 0 else "success",
                ),
            ]
        )

    return True, f"حجوزات العروسة: {customer_name}", content


def build_dress_bookings_view(dress_code, bookings_records, b_cols, normalize_code):
    """Build details modal content for dress bookings from stores."""
    dress_col = b_cols[5] if len(b_cols) > 5 else None
    normalized_code = normalize_code(dress_code)
    filtered = [
        row for row in rows(bookings_records)
        if dress_col and normalize_code(row.get(dress_col)) == normalized_code
    ]

    if not filtered:
        content = dbc.Alert("لا توجد حجوزات لهذا الفستان", color="warning")
    else:
        booking_id_col = b_cols[0] if len(b_cols) > 0 else None
        customer_col = b_cols[2] if len(b_cols) > 2 else None
        service_col = b_cols[4] if len(b_cols) > 4 else None
        event_date_col = b_cols[6] if len(b_cols) > 6 else None
        price_col = b_cols[7] if len(b_cols) > 7 else None
        remaining_col = b_cols[9] if len(b_cols) > 9 else None
        total_remaining = sum(float_value(row.get(remaining_col, 0)) for row in filtered) if remaining_col else 0.0

        table = dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("كود الحجز"),
                            html.Th("اسم العروسه"),
                            html.Th("الخدمة"),
                            html.Th("تاريخ المناسبة"),
                            html.Th("السعر"),
                            html.Th("المتبقي"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(row.get(booking_id_col, "")),
                                html.Td(row.get(customer_col, "")),
                                html.Td(row.get(service_col, "")),
                                html.Td(row.get(event_date_col, "")),
                                html.Td(f"{row.get(price_col, 0)} ج"),
                                html.Td(
                                    f"{row.get(remaining_col, 0)} ج",
                                    style={
                                        "fontWeight": "bold",
                                        "color": "red" if float_value(row.get(remaining_col, 0)) > 0 else "green",
                                    },
                                ),
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
                table,
                html.Hr(),
                dbc.Alert(
                    [
                        html.Strong("إجمالي المتبقي: "),
                        html.Span(
                            f"{total_remaining} ج",
                            style={
                                "fontSize": "1.2em",
                                "fontWeight": "bold",
                                "color": "red" if total_remaining > 0 else "green",
                            },
                        ),
                    ],
                    color="warning" if total_remaining > 0 else "success",
                ),
            ]
        )

    return True, f"حجوزات الفستان: {dress_code}", content
