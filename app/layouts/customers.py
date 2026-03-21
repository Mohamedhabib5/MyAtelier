from datetime import date

import dash_bootstrap_components as dbc
from dash import dcc, html


def layout_customers(get_customers_table_content, load_data, c_cols):
    customer_id_col = c_cols[0]
    customer_name_col = c_cols[2] if len(c_cols) > 2 else customer_id_col
    phone_col = c_cols[5] if len(c_cols) > 5 else customer_id_col

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.H3("👥 إدارة العملاء"), xs=12, md=6),
                    dbc.Col(
                        dbc.Button(
                            "➕ عميلة جديدة",
                            id="btn-add-customer-modal",
                            color="success",
                            className="page-action-btn",
                        ),
                        xs=12,
                        md=6,
                        className="text-md-end",
                    ),
                ],
                className="align-items-center g-3 mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="c-search",
                                            placeholder="🔍 ابحث عن عميلة (الاسم / الرقم)...",
                                            options=[
                                                {
                                                    "label": f"{r[customer_name_col]} ({r[phone_col]})",
                                                    "value": r[customer_id_col],
                                                }
                                                for _, r in load_data("customers.csv", c_cols).iterrows()
                                            ],
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
                                                    id="btn-edit-customer",
                                                    color="warning",
                                                    className="me-2",
                                                    disabled=True,
                                                ),
                                                dbc.Button(
                                                    "🗑️ حذف",
                                                    id="btn-delete-customer",
                                                    color="danger",
                                                    disabled=True,
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
            dcc.Store(id="c-edit-id", data=None),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("تأكيد الحذف")),
                    dbc.ModalBody("هل أنت متأكد من حذف هذه العميلة؟ لا يمكن التراجع عن هذا الإجراء."),
                    dbc.ModalFooter(
                        [
                            dbc.Button("تراجع", id="btn-cancel-delete", className="ms-auto", n_clicks=0),
                            dbc.Button("حذف نهائي", id="btn-confirm-delete", color="danger", n_clicks=0),
                        ]
                    ),
                ],
                id="modal-delete-customer",
                is_open=False,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="c-modal-title", children="إضافة عميلة جديدة")),
                    dbc.ModalBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("اسم العروسة *"), dbc.Input(id="c-name", placeholder="الاسم ثلاثي")],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                    dbc.Col(
                                        [dbc.Label("اسم العريس *"), dbc.Input(id="c-groom", placeholder="الاسم ثلاثي")],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                ],
                                className="g-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("رقم الهاتف 1 *"), dbc.Input(id="c-phone1", placeholder="01xxxxxxxxx")],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                    dbc.Col(
                                        [dbc.Label("رقم الهاتف 2"), dbc.Input(id="c-phone2", placeholder="01xxxxxxxxx")],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                ],
                                className="g-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("العنوان *"), dbc.Input(id="c-addr", placeholder="العنوان بالتفصيل")],
                                        xs=12,
                                        md=8,
                                        className="mb-3",
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("تاريخ التسجيل"),
                                            dbc.Input(id="c-reg-date", type="date", value=str(date.today())),
                                        ],
                                        xs=12,
                                        md=4,
                                        className="mb-3",
                                    ),
                                ],
                                className="g-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("ملاحظات"),
                                            dbc.Textarea(
                                                id="c-notes",
                                                placeholder="أي ملاحظات إضافية...",
                                                style={"height": "100px"},
                                            ),
                                        ],
                                        width=12,
                                        className="mb-3",
                                    ),
                                ]
                            ),
                            html.Div(id="c-add-alert"),
                        ]
                    ),
                    dbc.ModalFooter(dbc.Button("حفظ", id="btn-save-customer", color="primary", className="page-action-btn")),
                ],
                id="modal-customer",
                is_open=False,
                fullscreen="md-down",
                scrollable=True,
                className="form-modal",
            ),
            html.Div(id="customers-table-container", children=get_customers_table_content()),
        ]
    )
