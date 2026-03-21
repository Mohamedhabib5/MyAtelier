from datetime import date

import dash_bootstrap_components as dbc
from dash import dcc, html


def layout_payments(get_payments_table_content):
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.H3("💰 إدارة المدفوعات"), xs=12, md=6),
                    dbc.Col(
                        dbc.Button(
                            "➕ دفعة جديدة",
                            id="btn-add-payment-modal",
                            color="success",
                            className="page-action-btn",
                            n_clicks=0,
                        ),
                        xs=12,
                        md=6,
                        className="text-md-end",
                    ),
                ],
                className="align-items-center g-3 mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="p-search",
                                            placeholder="🔍 ابحث عن دفعة (كود الدفعة / اسم العميل)...",
                                            options=[],
                                            searchable=True,
                                        ),
                                        xs=12,
                                        md=8,
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "✏️ تعديل",
                                                    id="btn-edit-payment",
                                                    color="warning",
                                                    className="me-2",
                                                    disabled=True,
                                                    n_clicks=0,
                                                ),
                                                dbc.Button(
                                                    "🗑️ حذف",
                                                    id="btn-delete-payment",
                                                    color="danger",
                                                    disabled=True,
                                                    n_clicks=0,
                                                ),
                                            ],
                                            className="toolbar-actions",
                                        ),
                                        xs=12,
                                        md=4,
                                    ),
                                ],
                                className="g-3 align-items-start",
                            )
                        ]
                    )
                ],
                className="mb-4 dropdown-card",
            ),
            dcc.Store(id="p-edit-id", data=None),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("تأكيد الحذف")),
                    dbc.ModalBody("هل أنت متأكد من حذف هذه الدفعة؟ سيتم إعادة المبلغ إلى المتبقي."),
                    dbc.ModalFooter(
                        [
                            dbc.Button("تراجع", id="btn-cancel-delete-p", className="ms-auto", n_clicks=0),
                            dbc.Button("حذف", id="btn-confirm-delete-p", color="danger", n_clicks=0),
                        ]
                    ),
                ],
                id="modal-delete-payment",
                is_open=False,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="p-modal-title", children="تسجيل دفعة جديدة")),
                    dbc.ModalBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("التاريخ"), dbc.Input(id="p-date", type="date", value=date.today().isoformat())],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                    dbc.Col(
                                        [dbc.Label("المبلغ"), dbc.Input(id="p-amount", type="number", placeholder="المبلغ *")],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                ],
                                className="g-3",
                            ),
                            dcc.Dropdown(
                                id="p-booking",
                                placeholder="ابحث عن حجز (الاسم / الكود)...",
                                className="mb-3",
                                searchable=True,
                            ),
                            html.Div(id="p-booking-details", className="mb-3 p-2 bg-light border rounded"),
                            dbc.Textarea(id="p-notes", placeholder="ملاحظات الدفعة"),
                            html.Div(id="p-alert", className="mt-3"),
                        ]
                    ),
                    dbc.ModalFooter(dbc.Button("حفظ الدفعة", id="btn-save-payment", color="primary", className="page-action-btn", n_clicks=0)),
                ],
                id="modal-payment",
                is_open=False,
                fullscreen="md-down",
                scrollable=True,
                className="form-modal",
            ),
            html.Div(id="payments-table-container", children=get_payments_table_content()),
        ]
    )
