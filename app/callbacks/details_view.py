"""Helpers for details-view callback action-cell detection."""

from dash import html
import dash_bootstrap_components as dbc


def parse_grid_cell_clicked(cell_clicked):
    """Return normalized fields from an AG Grid cell-click payload."""
    if not isinstance(cell_clicked, dict):
        return {
            "col_id": None,
            "field": None,
            "value": None,
            "row_id": None,
            "value_formatted": None,
            "displayed_value": None,
            "cell_class": None,
            "data_action": None,
            "data": {},
        }

    col_def = cell_clicked.get("colDef") or {}
    data = cell_clicked.get("data") or {}
    return {
        "col_id": cell_clicked.get("colId") or cell_clicked.get("columnId"),
        "field": cell_clicked.get("field") or col_def.get("field"),
        "value": cell_clicked.get("value"),
        "row_id": cell_clicked.get("rowId"),
        "value_formatted": cell_clicked.get("valueFormatted"),
        "displayed_value": cell_clicked.get("displayedValue"),
        "cell_class": col_def.get("cellClass"),
        "data_action": data.get("__action__"),
        "data": data,
    }


def _normalize_action_text(value):
    return str(value).strip() if value is not None else ""


def _is_action_cell_class(cell_class):
    return cell_class == "ag-action-cell" or (
        isinstance(cell_class, (list, tuple)) and "ag-action-cell" in cell_class
    )


def is_grid_action_click(
    parsed_cell,
    action_label,
    action_col_ids=(),
    *,
    include_action_field=True,
    include_action_cell_class=False,
    include_data_action=False,
    strip_values=False,
):
    """Check whether parsed AG Grid click payload represents an action-cell click."""
    col_id = parsed_cell.get("col_id")
    field = parsed_cell.get("field")
    value = parsed_cell.get("value")
    value_formatted = parsed_cell.get("value_formatted")
    displayed_value = parsed_cell.get("displayed_value")

    if col_id in action_col_ids:
        return True
    if include_action_field and field == "__action__":
        return True

    if strip_values:
        label = _normalize_action_text(action_label)
        value_matches = (
            _normalize_action_text(value) == label
            or _normalize_action_text(value_formatted) == label
            or _normalize_action_text(displayed_value) == label
        )
    else:
        value_matches = (
            value == action_label
            or value_formatted == action_label
            or displayed_value == action_label
        )
    if value_matches:
        return True

    if include_data_action:
        data_action = parsed_cell.get("data_action")
        if strip_values:
            if _normalize_action_text(data_action) == _normalize_action_text(action_label):
                return True
        elif data_action == action_label:
            return True

    if include_action_cell_class and _is_action_cell_class(parsed_cell.get("cell_class")):
        return True

    return False


def build_payments_view(booking_id, load_data, p_cols, b_cols):
    """Build details modal content for booking payments."""
    p_df = load_data("payments.csv", p_cols)
    filtered = p_df[p_df["كود الحجز"] == booking_id]

    if filtered.empty:
        content = dbc.Alert("لا توجد مدفوعات لهذا الحجز", color="warning")
    else:
        b_df = load_data("bookings.csv", b_cols)
        booking = b_df[b_df["كود الحجز"] == booking_id]
        remaining = booking.iloc[0]["المتبقي"] if not booking.empty else "غير معروف"

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
                                html.Td(row["كود الدفع"]),
                                html.Td(
                                    f"{row['القيمة المدفوعة']} ج",
                                    style={"fontWeight": "bold", "color": "green"},
                                ),
                                html.Td(row["التاريخ"]),
                                html.Td(row["ملاحظات الدفع"]),
                            ]
                        )
                        for _, row in filtered.iterrows()
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
                                "color": "red" if float(remaining) > 0 else "green",
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
                        f"{filtered['القيمة المدفوعة'].astype(float).sum()} ج",
                    ],
                    className="text-end",
                ),
            ]
        )

    return f"💰 مدفوعات الحجز: {booking_id}", content


def build_customer_bookings_view(customer_name, load_data, b_cols):
    """Build details modal content for customer bookings."""
    b_df = load_data("bookings.csv", b_cols)
    filtered = b_df[b_df["اسم العروسه"] == customer_name]

    if filtered.empty:
        content = dbc.Alert("لا توجد حجوزات لهذه العروسة", color="warning")
    else:
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
                                html.Td(row["كود الحجز"]),
                                html.Td(row["القسم"]),
                                html.Td(row["الخدمة"]),
                                html.Td(row["تاريخ المناسبة"]),
                                html.Td(f"{row['السعر المتفق']} ج"),
                                html.Td(
                                    f"{row['المتبقي']} ج",
                                    style={
                                        "fontWeight": "bold",
                                        "color": "red" if float(row["المتبقي"]) > 0 else "green",
                                    },
                                ),
                            ]
                        )
                        for _, row in filtered.iterrows()
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            striped=True,
            className="table-sm",
        )

        total_remaining = filtered["المتبقي"].astype(float).sum()
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

    return True, f"📋 حجوزات العروسة: {customer_name}", content


def build_dress_bookings_view(dress_code, load_data, b_cols, normalize_code):
    """Build details modal content for dress bookings."""
    b_df = load_data("bookings.csv", b_cols)
    code = normalize_code(dress_code)
    codes = b_df["كود الفستان"].apply(normalize_code)
    filtered = b_df[codes == code]

    if filtered.empty:
        content = dbc.Alert("لا توجد حجوزات لهذا الفستان", color="warning")
    else:
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
                                html.Td(row["كود الحجز"]),
                                html.Td(row["اسم العروسه"]),
                                html.Td(row["الخدمة"]),
                                html.Td(row["تاريخ المناسبة"]),
                                html.Td(f"{row['السعر المتفق']} ج"),
                                html.Td(
                                    f"{row['المتبقي']} ج",
                                    style={
                                        "fontWeight": "bold",
                                        "color": "red" if float(row["المتبقي"]) > 0 else "green",
                                    },
                                ),
                            ]
                        )
                        for _, row in filtered.iterrows()
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            striped=True,
            className="table-sm",
        )

        total_remaining = filtered["المتبقي"].astype(float).sum()
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

    return True, f"👗 حجوزات الفستان: {dress_code}", content


def build_booking_view(booking_id, load_data, b_cols):
    """Build details modal content for a single booking."""
    b_df = load_data("bookings.csv", b_cols)
    filtered = b_df[b_df["كود الحجز"] == booking_id]

    if filtered.empty:
        content = dbc.Alert("لم يتم العثور على الحجز", color="danger")
    else:
        row = filtered.iloc[0]
        content = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [html.Strong("العروسه: "), html.Span(row["اسم العروسه"])],
                            width=6,
                        ),
                        dbc.Col(
                            [html.Strong("القسم: "), html.Span(row["القسم"])],
                            width=6,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [html.Strong("الخدمة: "), html.Span(row["الخدمة"])],
                            width=6,
                        ),
                        dbc.Col(
                            [html.Strong("تاريخ المناسبة: "), html.Span(row["تاريخ المناسبة"])],
                            width=6,
                        ),
                    ],
                    className="mb-2",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Strong("السعر المتفق: "),
                                html.Span(
                                    f"{row['السعر المتفق']} ج",
                                    style={"fontSize": "1.1em"},
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Strong("المدفوع: "),
                                html.Span(
                                    f"{row['المدفوع']} ج",
                                    style={"fontSize": "1.1em", "color": "green"},
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Strong("المتبقي: "),
                                html.Span(
                                    f"{row['المتبقي']} ج",
                                    style={
                                        "fontSize": "1.2em",
                                        "fontWeight": "bold",
                                        "color": "red" if float(row["المتبقي"]) > 0 else "green",
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
                        html.P(
                            row["ملاحظات الحجز"] if row["ملاحظات الحجز"] else "لا توجد ملاحظات",
                            className="text-muted",
                        ),
                    ]
                ),
            ]
        )

    return True, f"📋 تفاصيل الحجز: {booking_id}", content
