import dash_bootstrap_components as dbc
from dash import dcc, html


def layout_users(user_role="admin"):
    is_admin = user_role == "admin"
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H3("👤 " + ("إدارة المستخدمين" if is_admin else "حسابي")),
                        xs=12,
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "إضافة مستخدم",
                            id="btn-add-user-modal",
                            color="primary",
                            className="page-action-btn",
                        ),
                        xs=12,
                        md=6,
                        className="text-md-end",
                        style={} if is_admin else {"display": "none"},
                    ),
                ],
                className="align-items-center g-3 mb-3",
            ),
            dbc.Alert(
                "هذه الشاشة مخصصة لإدارة المستخدمين." if is_admin else "يمكنك هنا تعديل بيانات حسابك فقط.",
                color="warning" if is_admin else "info",
            ),
            html.Div(id="users-alert", className="mb-2"),
            html.P("قائمة المستخدمين المسجلين:" if is_admin else "بيانات الحساب الحالي:"),
            html.Div(id="users-list-container"),
            dcc.Store(id="u-form-mode", data="add"),
            dcc.Store(id="u-edit-id", data=None),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="u-modal-title", children="إضافة مستخدم جديد")),
                    dbc.ModalBody(
                        [
                            html.Div(
                                [
                                    dbc.Label("اسم المستخدم"),
                                    dbc.Input(id="u-username", placeholder="مثال: user1", className="mb-2"),
                                ],
                                id="u-username-group",
                            ),
                            dbc.Label("الاسم الكامل"),
                            dbc.Input(id="u-full-name", placeholder="الاسم الظاهر", className="mb-2"),
                            dbc.Label("كلمة المرور"),
                            dbc.Input(id="u-password", type="password", placeholder="كلمة مرور قوية", className="mb-2"),
                            dbc.FormText("اترك كلمة المرور فارغة إذا كنت لا تريد تغييرها عند التعديل.", className="mb-2"),
                            html.Div(
                                [
                                    dbc.Label("الصلاحية"),
                                    dcc.Dropdown(
                                        id="u-role",
                                        options=[
                                            {"label": "admin", "value": "admin"},
                                            {"label": "user", "value": "user"},
                                        ],
                                        value="user",
                                        clearable=False,
                                    ),
                                ],
                                id="u-role-group",
                                style={} if is_admin else {"display": "none"},
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("إلغاء", id="btn-cancel-user", color="secondary", className="ms-auto"),
                            dbc.Button("حفظ", id="btn-save-user", color="success"),
                        ]
                    ),
                ],
                id="modal-user",
                is_open=False,
                fullscreen="md-down",
                scrollable=True,
                className="form-modal",
            ),
        ]
    )
