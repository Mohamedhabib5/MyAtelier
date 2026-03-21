import dash
import dash_bootstrap_components as dbc
from app.constants import APP_VERSION


EXTERNAL_STYLESHEETS = [
    dbc.themes.LITERA,
    "assets/custom.css",
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css",
]


def create_dash_app(app_name):
    return dash.Dash(
        app_name,
        external_stylesheets=EXTERNAL_STYLESHEETS,
        title=f"نظام إدارة الأتيليه v{APP_VERSION}",
        suppress_callback_exceptions=True,
    )
