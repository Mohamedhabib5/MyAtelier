from datetime import date

import dash_bootstrap_components as dbc
from dash import dcc, html


def build_custody_workflow_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(id="dc-workflow-title"), close_button=False),
            dbc.ModalBody(
                [
                    html.Div(
                        [
                            dcc.Dropdown(id="dc-booking", placeholder="اختر الحجز...", className="mb-3", searchable=True),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("قيمة التأمين"), dbc.Input(id="dc-deposit-amount", type="number", value=0)],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                    dbc.Col(
                                        [dbc.Label("نوع الضمان"), dbc.Input(id="dc-guarantee-type", placeholder="بطاقة / رخصة / غيره")],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                ],
                                className="g-3",
                            ),
                            dbc.Label("مرجع الضمان"),
                            dbc.Input(id="dc-guarantee-reference", className="mb-3", placeholder="رقم البطاقة أو أي مرجع"),
                            dbc.Label("ملاحظات"),
                            dbc.Textarea(id="dc-create-notes", className="mb-3"),
                        ],
                        id="dc-create-section",
                    ),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("التاريخ"), dbc.Input(id="dc-action-date", type="date", value=date.today().isoformat())],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                    dbc.Col(
                                        [dbc.Label("حالة العهدة عند التسليم"), dbc.Input(id="dc-action-condition", placeholder="وصف مختصر")],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                ],
                                className="g-3",
                            ),
                            dbc.Label("ملاحظات"),
                            dbc.Textarea(id="dc-action-notes", className="mb-3"),
                        ],
                        id="dc-action-section",
                    ),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("التاريخ"), dbc.Input(id="dc-return-date", type="date", value=date.today().isoformat())],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                    dbc.Col(
                                        [dbc.Label("حالة العهدة عند الاستلام"), dbc.Input(id="dc-return-condition", placeholder="وصف مختصر")],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                ],
                                className="g-3",
                            ),
                            dbc.RadioItems(
                                id="dc-return-damage",
                                options=[
                                    {"label": "استلام بحالة جيدة", "value": "clean"},
                                    {"label": "استلام مع تلفيات", "value": "damage"},
                                ],
                                value="clean",
                                className="mb-3",
                            ),
                            html.Div(
                                [
                                    dbc.Label("قيمة سند التعويض"),
                                    dbc.Input(id="dc-return-compensation", type="number", value=0),
                                    dbc.FormText("القيمة المقترحة تساوي مبلغ التأمين ويمكن تعديلها."),
                                ],
                                id="dc-return-compensation-wrap",
                                className="mb-3",
                            ),
                            dbc.Checklist(
                                id="dc-return-guarantee",
                                options=[{"label": "تم رد وثيقة الضمان", "value": "returned"}],
                                value=["returned"],
                                switch=True,
                                className="mb-3",
                            ),
                            dbc.Input(id="dc-return-guarantee-date", type="date", value=date.today().isoformat(), className="mb-3"),
                            dbc.Label("ملاحظات"),
                            dbc.Textarea(id="dc-return-notes", className="mb-3"),
                        ],
                        id="dc-return-section",
                    ),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("التاريخ"), dbc.Input(id="dc-service-date", type="date", value=date.today().isoformat())],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("الحالة الجديدة"),
                                            dcc.Dropdown(
                                                id="dc-service-status",
                                                options=[
                                                    {"label": "في المغسلة", "value": "في المغسلة"},
                                                    {"label": "تحت الصيانة", "value": "تحت الصيانة"},
                                                    {"label": "متاح للإيجار", "value": "متاح للإيجار"},
                                                ],
                                                value="في المغسلة",
                                                clearable=False,
                                            ),
                                        ],
                                        xs=12,
                                        md=6,
                                        className="mb-3",
                                    ),
                                ],
                                className="g-3",
                            ),
                            dbc.Label("ملاحظات"),
                            dbc.Textarea(id="dc-service-notes", className="mb-3"),
                        ],
                        id="dc-service-section",
                    ),
                    html.Div(id="dc-workflow-alert"),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("إلغاء", id="btn-close-custody-workflow", color="secondary", outline=True, className="me-auto", n_clicks=0),
                    dbc.Button(id="btn-save-custody-workflow", color="primary", className="page-action-btn", n_clicks=0),
                ]
            ),
        ],
        id="modal-custody-workflow",
        is_open=False,
        fullscreen="md-down",
        scrollable=True,
        backdrop="static",
        className="form-modal",
    )


def layout_dress_custody(get_dress_custody_table_content):
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.H3("التسليم والاستلام"), xs=12, md=6),
                    dbc.Col(
                        dbc.Button("فتح سجل جديد", id="btn-open-custody-modal", color="primary", className="page-action-btn", n_clicks=0),
                        xs=12,
                        md=6,
                        className="text-md-end",
                    ),
                ],
                className="align-items-center g-3 mb-3",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="dc-search",
                                        placeholder="ابحث عن سجل (الحجز / العميل / الفستان)...",
                                        options=[],
                                        searchable=True,
                                    ),
                                    xs=12,
                                    lg=8,
                                    className="custody-search-col",
                                ),
                                dbc.Col(
                                    dbc.RadioItems(
                                        id="dc-stage-filter",
                                        options=[
                                            {"label": "عند العميل", "value": "customer"},
                                            {"label": "المغسلة والصيانة", "value": "service"},
                                            {"label": "مغلقة", "value": "closed"},
                                        ],
                                        value="customer",
                                        inline=True,
                                        className="custody-stage-filter",
                                    ),
                                    xs=12,
                                    lg=4,
                                ),
                            ],
                            className="g-3 align-items-start",
                        )
                    ]
                ),
                className="mb-4 dropdown-card",
            ),
            dbc.Card(dbc.CardBody(html.Div(id="dc-summary", children="اختر سجلًا لعرض التفاصيل.")), className="mb-4"),
            dcc.Store(
                id="dc-workflow-state",
                data={
                    "selected_custody_id": None,
                    "modal_kind": None,
                    "modal_open": False,
                    "prefill_data": {},
                    "alert": None,
                },
            ),
            build_custody_workflow_modal(),
            html.Div(id="dress-custody-table-container", children=get_dress_custody_table_content()),
        ]
    )
