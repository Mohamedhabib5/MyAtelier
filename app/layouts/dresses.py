from datetime import date

import dash_bootstrap_components as dbc
from dash import dcc, html


def layout_dresses(get_dresses_table_content):
    return html.Div([
        dbc.Row([
            dbc.Col(html.H3("👗 إدارة الفساتين"), xs=12, md=6),
            dbc.Col(
                dbc.Button("➕ فستان جديد", id="btn-add-dress-modal", color="warning", className="page-action-btn", n_clicks=0),
                xs=12,
                md=6,
                className="text-md-end",
            ),
        ], className="align-items-center g-3 mb-3"),
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(
                            id="d-search",
                            placeholder="🔍 ابحث عن فستان (الكود)...",
                            options=[],
                            searchable=True,
                        ),
                        xs=12,
                        md=8,
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Button("✏️ تعديل", id="btn-edit-dress", color="warning", className="me-2", disabled=True, n_clicks=0),
                            dbc.Button("🗑️ حذف", id="btn-delete-dress", color="danger", disabled=True, n_clicks=0),
                        ], className="toolbar-actions"),
                        xs=12,
                        md=4,
                    ),
                ], className="g-3 align-items-start"),
            ]),
        ], className="mb-4 dropdown-card"),
        dcc.Store(id="d-edit-id", data=None),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("تأكيد الحذف")),
            dbc.ModalBody("هل أنت متأكد من حذف هذا الفستان؟"),
            dbc.ModalFooter([
                dbc.Button("تراجع", id="btn-cancel-delete-d", className="ms-auto", n_clicks=0),
                dbc.Button("حذف", id="btn-confirm-delete-d", color="danger", n_clicks=0),
            ]),
        ], id="modal-delete-dress", is_open=False),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="d-modal-title", children="إضافة فستان جديد")),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col(dbc.Input(id="d-code", placeholder="كود الفستان *"), xs=12, md=6, className="mb-3"),
                    dbc.Col(dbc.Select(
                        id="d-type",
                        options=[
                            {"label": "زفاف", "value": "زفاف"},
                            {"label": "سوارية", "value": "سوارية"},
                            {"label": "غير محدد", "value": "غير محدد"},
                        ],
                        value="زفاف",
                    ), xs=12, md=6, className="mb-3"),
                    dbc.Col(dbc.Input(id="d-date", type="date", value=date.today().isoformat()), xs=12, md=6, className="mb-3"),
                    dbc.Col(dbc.Select(
                        id="d-status",
                        options=[
                            {"label": "متاح", "value": "متاح"},
                            {"label": "محجوز", "value": "محجوز"},
                            {"label": "في المغسلة", "value": "في المغسلة"},
                        ],
                        value="متاح",
                    ), xs=12, md=6, className="mb-3"),
                    dbc.Col(dbc.Textarea(id="d-desc", placeholder="وصف الفستان *"), width=12, className="mb-3"),
                    dbc.Col([
                        dbc.Label("صورة الفستان (MAX 300KB)"),
                        dcc.Upload(
                            id="d-upload-image",
                            children=dbc.Button("رفع صورة", color="secondary", outline=True, size="sm", className="w-100"),
                            style={
                                "width": "100%",
                                "height": "40px",
                                "lineHeight": "40px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                            },
                            multiple=False,
                        ),
                        html.Div(id="d-upload-output", style={"fontSize": "0.8rem", "color": "green", "marginTop": "5px"}),
                    ], width=12, className="mb-3"),
                ], className="g-3"),
                html.Div(id="d-alert"),
            ]),
            dbc.ModalFooter(dbc.Button("حفظ", id="btn-save-dress", color="primary", className="page-action-btn", n_clicks=0)),
        ], id="modal-dress", is_open=False, fullscreen="md-down", scrollable=True, className="form-modal"),
        html.Div(id="dresses-table-container", children=get_dresses_table_content()),
    ])
