from dash import Input, Output, State, ctx, no_update
from flask import session as flask_session


def register_navigation_callbacks(app):
    @app.callback(
        [Output("main-tabs", "active_tab"), Output("mobile-menu-state", "data", allow_duplicate=True)],
        [
            Input("nav-finance", "n_clicks"),
            Input("nav-bookings", "n_clicks"),
            Input("nav-customers", "n_clicks"),
            Input("nav-services", "n_clicks"),
            Input("nav-dresses", "n_clicks"),
            Input("nav-payments", "n_clicks"),
            Input("nav-settings", "n_clicks"),
            Input("nav-users", "n_clicks"),
            Input("mb-finance", "n_clicks"),
            Input("mb-bookings", "n_clicks"),
            Input("mb-customers", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def switch_tab(_n1, _n2, _n3, _n4, _n5, _n6, _n7, _n8, _m1, _m2, _m3):
        ctx_id = ctx.triggered_id
        if not ctx_id:
            return no_update, no_update

        mapping = {
            "nav-finance": "tab-finance",
            "mb-finance": "tab-finance",
            "nav-bookings": "tab-bookings",
            "mb-bookings": "tab-bookings",
            "nav-customers": "tab-customers",
            "mb-customers": "tab-customers",
            "nav-services": "tab-services",
            "nav-dresses": "tab-dresses",
            "nav-payments": "tab-payments",
            "nav-settings": "tab-settings",
            "nav-users": "tab-users",
        }
        target_tab = mapping.get(ctx_id, no_update)
        if target_tab is no_update:
            return no_update, no_update
        return target_tab, False

    @app.callback(
        [
            Output("nav-finance", "className"),
            Output("nav-bookings", "className"),
            Output("nav-customers", "className"),
            Output("nav-services", "className"),
            Output("nav-dresses", "className"),
            Output("nav-payments", "className"),
            Output("nav-settings", "className"),
            Output("nav-users", "className"),
            Output("mb-finance", "className"),
            Output("mb-bookings", "className"),
            Output("mb-customers", "className"),
            Output("mb-logout", "className"),
            Output("mb-menu", "className"),
        ],
        Input("main-tabs", "active_tab"),
    )
    def update_active_nav(active_tab):
        valid_tabs = {
            "tab-finance",
            "tab-bookings",
            "tab-customers",
            "tab-services",
            "tab-dresses",
            "tab-payments",
            "tab-settings",
            "tab-users",
        }
        if active_tab not in valid_tabs:
            active_tab = "tab-finance"
        default_class = "nav-link"
        active_class = "nav-link active"
        nav_classes = [
            active_class if t == active_tab else default_class
            for t in [
                "tab-finance",
                "tab-bookings",
                "tab-customers",
                "tab-services",
                "tab-dresses",
                "tab-payments",
                "tab-settings",
                "tab-users",
            ]
        ]
        bottom_map = {
            "tab-finance": "mb-finance",
            "tab-bookings": "mb-bookings",
            "tab-customers": "mb-customers",
        }
        active_bottom = bottom_map.get(active_tab, "mb-menu")
        bottom_classes = [
            "bottom-nav-item active" if item_id == active_bottom else "bottom-nav-item"
            for item_id in ["mb-finance", "mb-bookings", "mb-customers", "mb-logout", "mb-menu"]
        ]
        bottom_classes[3] += " text-danger"
        return [*nav_classes, *bottom_classes]

    @app.callback(
        [
            Output("view-finance", "style"),
            Output("view-bookings", "style"),
            Output("view-customers", "style"),
            Output("view-services", "style"),
            Output("view-dresses", "style"),
            Output("view-payments", "style"),
            Output("view-settings", "style"),
            Output("view-users", "style"),
        ],
        Input("main-tabs", "active_tab"),
    )
    def show_hide_tabs(active_tab):
        tabs = [
            "tab-finance",
            "tab-bookings",
            "tab-customers",
            "tab-services",
            "tab-dresses",
            "tab-payments",
            "tab-settings",
            "tab-users",
        ]
        if active_tab not in tabs:
            active_tab = "tab-finance"
        styles = [{"display": "none"} for _ in tabs]
        styles[tabs.index(active_tab)] = {"display": "block"}
        return styles

    @app.callback(
        [
            Output("modal-booking", "is_open", allow_duplicate=True),
            Output("modal-delete-booking", "is_open", allow_duplicate=True),
            Output("modal-customer", "is_open", allow_duplicate=True),
            Output("modal-delete-customer", "is_open", allow_duplicate=True),
            Output("modal-service", "is_open", allow_duplicate=True),
            Output("modal-delete-service", "is_open", allow_duplicate=True),
            Output("modal-dress", "is_open", allow_duplicate=True),
            Output("modal-delete-dress", "is_open", allow_duplicate=True),
            Output("modal-payment", "is_open", allow_duplicate=True),
            Output("modal-delete-payment", "is_open", allow_duplicate=True),
        ],
        Input("main-tabs", "active_tab"),
        prevent_initial_call=True,
    )
    def close_all_entry_modals_on_tab_change(_active_tab):
        return (False,) * 10


def register_sidebar_clientside_callback(app):
    @app.callback(
        Output("mobile-menu-state", "data"),
        [
            Input("btn-sidebar-toggle", "n_clicks"),
            Input("mb-menu", "n_clicks"),
            Input("sidebar-backdrop", "n_clicks"),
            Input("btn-sidebar-close-escape", "n_clicks"),
        ],
        State("mobile-menu-state", "data"),
        prevent_initial_call=True,
    )
    def toggle_sidebar_state(_n_top, _n_bottom, _n_backdrop, _n_escape, is_open):
        trigger = ctx.triggered_id
        if trigger in {"sidebar-backdrop", "btn-sidebar-close-escape"}:
            return False
        return not bool(is_open)

    @app.callback(
        [
            Output("app-shell", "className"),
            Output("sidebar-container", "className"),
            Output("sidebar-backdrop", "className"),
        ],
        Input("mobile-menu-state", "data"),
    )
    def sync_sidebar_shell(is_open):
        if is_open:
            return "app-shell mobile-menu-open", "sidebar sidebar-open", "sidebar-backdrop show"
        return "app-shell", "sidebar", "sidebar-backdrop"
