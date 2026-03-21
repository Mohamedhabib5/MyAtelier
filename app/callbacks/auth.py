from dash import Input, Output, State, html, no_update
import dash_bootstrap_components as dbc
from flask import session as flask_session
import re
import time
import logic


def register_auth_callbacks(
    app,
    login_layout,
    main_layout,
    check_users,
    verify_password,
):
    @app.callback(
        Output("user_session_store", "data", allow_duplicate=True),
        [
            Input("logout-btn", "n_clicks"),
            Input("logout-btn-mobile", "n_clicks"),
            Input("mb-logout", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def logout(n1, n2, n3):
        if not n1 and not n2 and not n3:
            return no_update
        flask_session.clear()
        return None

    @app.callback(
        Output("page-content", "children"),
        [Input("user_session_store", "data"), Input("url", "pathname")],
    )
    def display_page(session_data, _pathname):
        try:
            server_logged_in = bool(flask_session.get("logged_in"))
            server_role = flask_session.get("role")
            server_full_name = flask_session.get("full_name")
            server_username = flask_session.get("username")

            if (
                not server_logged_in
                or not server_role
                or not server_full_name
            ):
                return login_layout
            user_data = {
                "logged_in": True,
                "username": server_username,
                "full_name": server_full_name,
                "role": server_role,
            }
            return main_layout(user_data)
        except Exception as e:
            import traceback

            print("=" * 80)
            print("ERROR IN display_page CALLBACK:")
            print(traceback.format_exc())
            print("=" * 80)
            return html.Div([html.H1("خطأ أثناء تحميل الصفحة"), html.Pre(str(e))])

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
        Input("user_session_store", "data"),
        prevent_initial_call=True,
    )
    def close_all_entry_modals_on_login(session_data):
        if not isinstance(session_data, dict) or not session_data.get("logged_in"):
            return (no_update,) * 10
        return (False,) * 10

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
        Input("page-content", "children"),
        State("user_session_store", "data"),
        prevent_initial_call=True,
    )
    def close_all_entry_modals_after_main_mount(_page_children, session_data):
        if not isinstance(session_data, dict) or not session_data.get("logged_in"):
            return (no_update,) * 10
        return (False,) * 10

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
        Input("post-login-modal-reset", "n_intervals"),
        State("user_session_store", "data"),
        prevent_initial_call=True,
    )
    def close_all_entry_modals_after_post_login_interval(_tick, session_data):
        if not isinstance(session_data, dict) or not session_data.get("logged_in"):
            return (no_update,) * 10
        return (False,) * 10

    @app.callback(
        [
            Output("btn-add-booking-modal", "n_clicks", allow_duplicate=True),
            Output("btn-edit-booking", "n_clicks", allow_duplicate=True),
            Output("btn-save-booking", "n_clicks", allow_duplicate=True),
            Output("btn-delete-booking", "n_clicks", allow_duplicate=True),
            Output("btn-cancel-delete-b", "n_clicks", allow_duplicate=True),
            Output("btn-confirm-delete-b", "n_clicks", allow_duplicate=True),
            Output("btn-add-service-modal", "n_clicks", allow_duplicate=True),
            Output("btn-edit-service", "n_clicks", allow_duplicate=True),
            Output("btn-save-service", "n_clicks", allow_duplicate=True),
            Output("btn-delete-service", "n_clicks", allow_duplicate=True),
            Output("btn-cancel-delete-s", "n_clicks", allow_duplicate=True),
            Output("btn-confirm-delete-s", "n_clicks", allow_duplicate=True),
            Output("btn-add-dress-modal", "n_clicks", allow_duplicate=True),
            Output("btn-edit-dress", "n_clicks", allow_duplicate=True),
            Output("btn-save-dress", "n_clicks", allow_duplicate=True),
            Output("btn-delete-dress", "n_clicks", allow_duplicate=True),
            Output("btn-cancel-delete-d", "n_clicks", allow_duplicate=True),
            Output("btn-confirm-delete-d", "n_clicks", allow_duplicate=True),
            Output("btn-add-payment-modal", "n_clicks", allow_duplicate=True),
            Output("btn-edit-payment", "n_clicks", allow_duplicate=True),
            Output("btn-save-payment", "n_clicks", allow_duplicate=True),
            Output("btn-delete-payment", "n_clicks", allow_duplicate=True),
            Output("btn-cancel-delete-p", "n_clicks", allow_duplicate=True),
            Output("btn-confirm-delete-p", "n_clicks", allow_duplicate=True),
        ],
        Input("page-content", "children"),
        State("user_session_store", "data"),
        prevent_initial_call=True,
    )
    def reset_modal_button_clicks_after_login(_page_children, session_data):
        if not isinstance(session_data, dict) or not session_data.get("logged_in"):
            return (no_update,) * 24
        return (0,) * 24

    @app.callback(
        Output("main-tabs", "active_tab", allow_duplicate=True),
        Input("user_session_store", "data"),
        prevent_initial_call=True,
    )
    def force_default_tab_after_login(session_data):
        if not isinstance(session_data, dict) or not session_data.get("logged_in"):
            return no_update
        return "tab-finance"

    @app.callback(
        [
            Output("nav-finance", "n_clicks", allow_duplicate=True),
            Output("nav-bookings", "n_clicks", allow_duplicate=True),
            Output("nav-customers", "n_clicks", allow_duplicate=True),
            Output("nav-services", "n_clicks", allow_duplicate=True),
            Output("nav-dresses", "n_clicks", allow_duplicate=True),
            Output("nav-payments", "n_clicks", allow_duplicate=True),
            Output("nav-settings", "n_clicks", allow_duplicate=True),
            Output("nav-users", "n_clicks", allow_duplicate=True),
            Output("mb-finance", "n_clicks", allow_duplicate=True),
            Output("mb-bookings", "n_clicks", allow_duplicate=True),
            Output("mb-customers", "n_clicks", allow_duplicate=True),
        ],
        Input("page-content", "children"),
        State("user_session_store", "data"),
        prevent_initial_call=True,
    )
    def reset_nav_clicks_after_login(_page_children, session_data):
        if not isinstance(session_data, dict) or not session_data.get("logged_in"):
            return (no_update,) * 11
        return (0,) * 11

    @app.callback(
        [Output("user_session_store", "data"), Output("login-alert", "children")],
        [Input("login-btn", "n_clicks")],
        [State("login-username", "value"), State("login-password", "value")],
        prevent_initial_call=True,
    )
    def login(n_clicks, username, password):
        if not n_clicks:
            return no_update, ""
        if not username or not password:
            return no_update, dbc.Alert("\u26a0\ufe0f \u0627\u0644\u0631\u062c\u0627\u0621 \u0625\u062f\u062e\u0627\u0644 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a", color="warning")

        users = check_users()
        user = users[users["username"] == username]
        if not user.empty and verify_password(password, user.iloc[0]["password_hash"]):
            # Auto-upgrade legacy SHA256 hashes after a successful login.
            try:
                stored_hash = str(user.iloc[0]["password_hash"] or "").strip()
                if re.fullmatch(r"[0-9a-fA-F]{64}", stored_hash):
                    upgraded_hash = logic.hash_password(password)
                    logic.update_user_password_hash(username, upgraded_hash)
            except Exception:
                # Non-blocking: login should still succeed even if upgrade fails.
                pass

            flask_session["logged_in"] = True
            flask_session["username"] = username
            flask_session["full_name"] = user.iloc[0]["full_name"]
            flask_session["role"] = user.iloc[0]["role"]
            session_data = {"logged_in": True, "login_ts": int(time.time() * 1000)}
            return session_data, ""

        return no_update, dbc.Alert("\u274c \u0628\u064a\u0627\u0646\u0627\u062a \u063a\u064a\u0631 \u0635\u062d\u064a\u062d\u0629", color="danger")

