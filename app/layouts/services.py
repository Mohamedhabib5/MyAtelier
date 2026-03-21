import dash_bootstrap_components as dbc
from dash import dcc, html


def layout_services(get_services_table_content, check_departments):
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.H3("✂️ إدارة الخدمات"), xs=12, md=6),
                    dbc.Col(
                        dbc.Button("➕ خدمة جديدة", id="btn-add-service-modal", color="info", className="page-action-btn", n_clicks=0),
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
                                            id="s-search",
                                            placeholder="🔍 ابحث عن خدمة...",
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
                                                    id="btn-edit-service",
                                                    color="warning",
                                                    className="me-2",
                                                    disabled=True,
                                                    n_clicks=0,
                                                ),
                                                dbc.Button(
                                                    "🗑️ حذف",
                                                    id="btn-delete-service",
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
            dcc.Store(id="s-edit-id", data=None),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("تأكيد الحذف")),
                    dbc.ModalBody("هل أنت متأكد من حذف هذه الخدمة؟"),
                    dbc.ModalFooter(
                        [
                            dbc.Button("تراجع", id="btn-cancel-delete-s", className="ms-auto", n_clicks=0),
                            dbc.Button("حذف", id="btn-confirm-delete-s", color="danger", n_clicks=0),
                        ]
                    ),
                ],
                id="modal-delete-service",
                is_open=False,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="s-modal-title", children="إضافة خدمة جديدة")),
                    dbc.ModalBody(
                        [
                            dbc.Input(id="s-name", placeholder="اسم الخدمة *", className="mb-3"),
                            dcc.Dropdown(
                                id="s-dept",
                                options=[
                                    {"label": d, "value": d}
                                    for d in check_departments()["department_name"]
                                ],
                                placeholder="اختر القسم...",
                                className="mb-3",
                                searchable=True,
                            ),
                            dbc.Input(
                                id="s-price",
                                type="number",
                                placeholder="السعر المقترح",
                                className="mb-3",
                            ),
                            html.Div(id="s-alert"),
                        ]
                    ),
                    dbc.ModalFooter(dbc.Button("حفظ", id="btn-save-service", color="primary", className="page-action-btn", n_clicks=0)),
                ],
                id="modal-service",
                is_open=False,
                fullscreen="md-down",
                scrollable=True,
                className="form-modal",
            ),
            html.Div(id="services-table-container", children=get_services_table_content()),
        ]
    )
