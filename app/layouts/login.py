import dash_bootstrap_components as dbc
from dash import html


def layout_login():
    return dbc.Container([
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H2("🔒 نظام إدارة الأتيلية", className="text-center mb-4", style={"color": "#667eea"}),
                        dbc.Input(id="login-username", placeholder="اسم المستخدم", type="text", className="mb-3"),
                        dbc.Input(id="login-password", placeholder="كلمة المرور", type="password", className="mb-3"),
                        dbc.Button("دخول 🚀", id="login-btn", color="primary", className="w-100"),
                        html.Div(id="login-alert", className="mt-3"),
                    ])
                ], style={"maxWidth": "500px", "margin": "100px auto", "padding": "20px"}),
                width=12,
            )
        )
    ], fluid=True)
