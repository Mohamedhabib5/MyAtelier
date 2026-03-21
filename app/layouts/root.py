import dash_bootstrap_components as dbc
from dash import dcc, html


def layout_root():
    return html.Div([
        dcc.Store(id="user_session_store", storage_type="session"),
        dcc.Store(id="last-added-customer", data=None),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
        html.Div(
            dbc.Toast(
                id="app-success-toast",
                header="\u062a\u0645 \u0627\u0644\u062d\u0641\u0638",
                children="\u062a\u0645\u062a \u0627\u0644\u0639\u0645\u0644\u064a\u0629 \u0628\u0646\u062c\u0627\u062d",
                is_open=False,
                dismissable=True,
                duration=3000,
                icon="success",
            ),
            id="app-toast-container",
            style={"position": "fixed", "top": "1rem", "left": "1rem", "zIndex": 1060},
        ),
    ])
