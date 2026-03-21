import dash_bootstrap_components as dbc
from dash import dcc, html
from app.constants import APP_VERSION
import logic


def layout_main(
    user_data,
    *,
    layout_finance,
    layout_bookings,
    check_departments,
    get_bookings_table_content,
    layout_customers,
    get_customers_table_content,
    load_data,
    c_cols,
    layout_services,
    get_services_table_content,
    layout_dresses,
    get_dresses_table_content,
    layout_payments,
    get_payments_table_content,
    layout_settings,
    backup_folder,
    get_dept_table_content,
    layout_users,
):
    company_name = logic.get_company_name()
    user_role = user_data.get("role")
    user_full_name = user_data.get("full_name") or user_data.get("username", "")
    users_nav_label = "المستخدمين" if user_role == "admin" else "حسابي"
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3(company_name, id="app-title-desktop", className="mb-0"),
                                    html.Small(
                                        f"Management Dashboard v{APP_VERSION}",
                                        className="text-muted",
                                        style={"color": "rgba(255,255,255,0.5) !important"},
                                    ),
                                ],
                                className="sidebar-header",
                            ),
                            html.Div(
                                [
                                    dbc.NavLink([html.I(className="bi bi-house-door-fill"), "\u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629"], href="#", id="nav-finance", n_clicks=0, className="nav-link"),
                                    dbc.NavLink([html.I(className="bi bi-calendar-check-fill"), "\u0627\u0644\u062d\u062c\u0648\u0632\u0627\u062a"], href="#", id="nav-bookings", n_clicks=0, className="nav-link"),
                                    dbc.NavLink([html.I(className="bi bi-people-fill"), "\u0627\u0644\u0639\u0645\u0644\u0627\u0621"], href="#", id="nav-customers", n_clicks=0, className="nav-link"),
                                    dbc.NavLink([html.I(className="bi bi-scissors"), "\u0627\u0644\u062e\u062f\u0645\u0627\u062a"], href="#", id="nav-services", n_clicks=0, className="nav-link"),
                                    dbc.NavLink([html.I(className="bi bi-gem"), "\u0627\u0644\u0641\u0633\u0627\u062a\u064a\u0646"], href="#", id="nav-dresses", n_clicks=0, className="nav-link"),
                                    dbc.NavLink([html.I(className="bi bi-cash-stack"), "\u0627\u0644\u0645\u062f\u0641\u0648\u0639\u0627\u062a"], href="#", id="nav-payments", n_clicks=0, className="nav-link"),
                                    dbc.NavLink([html.I(className="bi bi-gear-fill"), "\u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a"], href="#", id="nav-settings", n_clicks=0, className="nav-link"),
                                    dbc.NavLink(
                                        [html.I(className="bi bi-person-badge-fill"), users_nav_label],
                                        href="#",
                                        id="nav-users",
                                        n_clicks=0,
                                        className="nav-link",
                                    ),
                                ],
                                className="flex-grow-1",
                            ),
                            html.Div(
                                [
                                    html.Hr(style={"borderColor": "rgba(255,255,255,0.1)"}),
                                    html.Div(
                                        [
                                            html.I(className="bi bi-person-circle fs-4 me-2"),
                                            html.Span(user_full_name, className="fw-bold"),
                                        ],
                                        className="d-flex align-items-center mb-3 text-white",
                                    ),
                                    dbc.Button([html.I(className="bi bi-box-arrow-right"), " \u062e\u0631\u0648\u062c"], id="logout-btn", color="danger", className="w-100 btn-sm"),
                                ]
                            ),
                        ],
                        id="sidebar-container",
                        className="sidebar",
                    ),
                    html.Div(id="sidebar-backdrop", className="sidebar-backdrop", n_clicks=0),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Button(html.I(className="bi bi-box-arrow-right fs-4"), id="logout-btn-mobile", color="link", className="text-danger p-0 me-3"),
                                                    html.Span(company_name, id="app-title-mobile", className="h5 text-primary fw-bold m-0"),
                                                ],
                                                width=8,
                                                className="d-flex align-items-center",
                                            ),
                                            dbc.Col(
                                                dbc.Button(html.I(className="bi bi-list fs-1"), id="btn-sidebar-toggle", color="link", className="text-dark p-0"),
                                                width=4,
                                                className="text-end",
                                            ),
                                        ],
                                        align="center",
                                    ),
                                ],
                                className="mobile-topbar d-lg-none bg-white p-3 shadow-sm mb-3 sticky-top",
                            ),
                            dbc.Container(
                                [
                                    dbc.Tabs(
                                        [
                                            dbc.Tab(tab_id="tab-finance"),
                                            dbc.Tab(tab_id="tab-bookings"),
                                            dbc.Tab(tab_id="tab-customers"),
                                            dbc.Tab(tab_id="tab-services"),
                                            dbc.Tab(tab_id="tab-dresses"),
                                            dbc.Tab(tab_id="tab-payments"),
                                            dbc.Tab(tab_id="tab-settings"),
                                            dbc.Tab(tab_id="tab-users"),
                                        ],
                                        id="main-tabs",
                                        active_tab="tab-finance",
                                        style={"display": "none"},
                                    ),
                                    html.Div(
                                        id="tab-content",
                                        className="fade-in",
                                        children=[
                                            html.Div(layout_finance(), id="view-finance", style={"display": "block"}),
                                            html.Div(layout_bookings(check_departments, get_bookings_table_content), id="view-bookings", style={"display": "none"}),
                                            html.Div(layout_customers(get_customers_table_content, load_data, c_cols), id="view-customers", style={"display": "none"}),
                                            html.Div(layout_services(get_services_table_content, check_departments), id="view-services", style={"display": "none"}),
                                            html.Div(layout_dresses(get_dresses_table_content), id="view-dresses", style={"display": "none"}),
                                            html.Div(layout_payments(get_payments_table_content), id="view-payments", style={"display": "none"}),
                                            html.Div(layout_settings(backup_folder, get_dept_table_content), id="view-settings", style={"display": "none"}),
                                            html.Div(layout_users(user_role), id="view-users", style={"display": "none"}),
                                        ],
                                    ),
                                ],
                                fluid=True,
                                className="py-2",
                            ),
                        ],
                        className="content",
                    ),
                    html.Div(
                        [
                            html.Div([html.I(className="bi bi-house-door-fill"), "\u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629"], id="mb-finance", className="bottom-nav-item active"),
                            html.Div([html.I(className="bi bi-calendar-check-fill"), "\u0627\u0644\u062d\u062c\u0648\u0632\u0627\u062a"], id="mb-bookings", className="bottom-nav-item"),
                            html.Div([html.I(className="bi bi-people-fill"), "\u0627\u0644\u0639\u0645\u0644\u0627\u0621"], id="mb-customers", className="bottom-nav-item"),
                            html.Div([html.I(className="bi bi-box-arrow-right"), "\u062e\u0631\u0648\u062c"], id="mb-logout", className="bottom-nav-item text-danger"),
                            html.Div([html.I(className="bi bi-list-ul"), "\u0627\u0644\u0642\u0627\u0626\u0645\u0629"], id="mb-menu", className="bottom-nav-item"),
                        ],
                        className="bottom-nav",
                    ),
                ],
                id="app-shell",
                className="app-shell",
            ),
            html.Button(id="btn-sidebar-close-escape", className="d-none", n_clicks=0),
            dcc.Store(id="mobile-menu-state", data=False),
            dcc.Store(id="customers_data", storage_type="memory"),
            dcc.Store(id="customers_version", data=0, storage_type="memory"),
            dcc.Store(id="services_data", storage_type="memory"),
            dcc.Store(id="services_version", data=0, storage_type="memory"),
            dcc.Store(id="bookings_data", storage_type="memory"),
            dcc.Store(id="bookings_version", data=0, storage_type="memory"),
            dcc.Store(id="payments_data", storage_type="memory"),
            dcc.Store(id="payments_version", data=0, storage_type="memory"),
            dcc.Store(id="dresses_data", storage_type="memory"),
            dcc.Store(id="dresses_version", data=0, storage_type="memory"),
            dcc.Store(id="finance_snapshots", storage_type="memory"),
            dcc.Interval(id="post-login-modal-reset", interval=900, n_intervals=0, max_intervals=1),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="details-viewer-title", children="\u0627\u0644\u062a\u0641\u0627\u0635\u064a\u0644")),
                dbc.ModalBody(id="details-viewer-body"),
                dbc.ModalFooter(dbc.Button("\u0625\u063a\u0644\u0627\u0642", id="btn-close-details", className="ms-auto", n_clicks=0)),
            ], id="modal-details-viewer", is_open=False, size="lg"),
        ]
    )
