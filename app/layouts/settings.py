import os

import dash_bootstrap_components as dbc
from dash import dcc, html
import logic


def layout_settings(backup_folder, get_dept_table_content):
    return html.Div(
        [
            html.H3("⚙️ الإعدادات"),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("إعداد اسم الشركة"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Input(
                                            id="company-name-input",
                                            value=logic.get_company_name(),
                                            placeholder="اسم الشركة",
                                        ),
                                        xs=12,
                                        md=8,
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Save",
                                            id="btn-save-company-name",
                                            color="primary",
                                            className="page-action-btn",
                                        ),
                                        xs=12,
                                        md=4,
                                    ),
                                ],
                                className="g-2",
                            ),
                            html.Div(id="company-name-alert", className="mt-3"),
                        ]
                    )
                ],
                className="mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("النسخ الاحتياطي"),
                            html.P(
                                "يتم إنشاء نسخة يدوية عند الضغط على زر النسخ مع إنشاء ملف ZIP تلقائياً."
                            ),
                            html.P(
                                f"مسار النسخ الاحتياطية: {os.path.abspath(backup_folder)}"
                            ),
                            dbc.Button(
                                "💾 إنشاء وتنزيل نسخة احتياطية",
                                id="btn-create-backup",
                                color="primary",
                                className="me-2",
                            ),
                            dbc.Button(
                                "📂 فتح مجلد النسخ الاحتياطية",
                                id="btn-open-backups",
                                color="secondary",
                                disabled=False,
                            ),
                            html.Div(id="backup-alert", className="mt-3"),
                            html.Div(id="backup-open-alert", className="mt-2"),
                            dcc.Download(id="backup-download"),
                        ]
                    )
                ],
                className="mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(html.H5("إدارة الأقسام"), xs=12, md=6),
                                    dbc.Col(
                                        dbc.Button(
                                            "➕ قسم جديد",
                                            id="btn-add-dept-modal",
                                            color="success",
                                            className="page-action-btn",
                                        ),
                                        xs=12,
                                        md=6,
                                        className="text-md-end",
                                    ),
                                ],
                                className="align-items-center g-3 mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="dept-search",
                                            placeholder="🔍 ابحث عن قسم...",
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
                                                    id="btn-edit-dept",
                                                    color="warning",
                                                    className="me-2",
                                                    disabled=True,
                                                ),
                                                dbc.Button(
                                                    "🗑️ حذف",
                                                    id="btn-delete-dept",
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
                                className="g-3 mb-3",
                            ),
                            dcc.Store(id="dept-edit-id", data=None),
                            html.Div(id="dept-alert"),
                            html.Div(id="dept-table-container", children=get_dept_table_content()),
                        ]
                    )
                ]
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            id="dept-modal-title",
                            children="إضافة قسم جديد",
                        )
                    ),
                    dbc.ModalBody(
                        [
                            dbc.Input(
                                id="dept-name",
                                placeholder="اسم القسم",
                                className="mb-3",
                            ),
                        ]
                    ),
                    dbc.ModalFooter(dbc.Button("حفظ", id="btn-save-dept", color="primary", className="page-action-btn")),
                ],
                id="modal-dept",
                is_open=False,
                fullscreen="md-down",
                scrollable=True,
                className="form-modal",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("تأكيد الحذف")),
                    dbc.ModalBody(
                        "هل أنت متأكد من حذف هذا القسم؟"
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "تراجع",
                                id="btn-cancel-delete-dept",
                                className="ms-auto",
                                n_clicks=0,
                            ),
                            dbc.Button(
                                "حذف",
                                id="btn-confirm-delete-dept",
                                color="danger",
                                n_clicks=0,
                            ),
                        ]
                    ),
                ],
                id="modal-delete-dept",
                is_open=False,
            ),
        ]
    )
