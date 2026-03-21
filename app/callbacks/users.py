from flask import session as flask_session

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, ctx, no_update

import logic


EDIT_ACTION_LABEL = "تعديل"


def _is_admin(role):
    return str(role or "").strip() == "admin"


def _role_group_style(role, form_mode):
    if _is_admin(role) and form_mode in {"add", "edit_admin"}:
        return {}
    return {"display": "none"}


def _username_disabled(role, form_mode):
    return (not _is_admin(role)) or form_mode == "edit_self"


def _build_users_table(actor_username, actor_role, create_dt):
    df = logic.list_visible_users(actor_username, actor_role)
    if df.empty:
        return dbc.Alert("لا توجد بيانات مستخدمين.", color="info")

    visible_cols = ["username", "full_name", "role", "created_date"] if _is_admin(actor_role) else [
        "username",
        "full_name",
        "created_date",
    ]
    return create_dt(
        df[visible_cols],
        table_id="users-table",
        action_buttons={
            "field": "__action__",
            "col_id": "edit-user-action",
            "label": EDIT_ACTION_LABEL,
            "mobile_type": "edit-user",
            "mobile_color": "warning",
            "header": "",
            "minWidth": 120,
            "maxWidth": 140,
        },
        row_id_field="username",
    )


def _is_edit_action_click(cell_clicked):
    if not cell_clicked:
        return False
    col_id = cell_clicked.get("colId") or cell_clicked.get("columnId")
    col_def = cell_clicked.get("colDef") or {}
    field = cell_clicked.get("field") or col_def.get("field")
    value = str(cell_clicked.get("value") or "").strip()
    cell_class = col_def.get("cellClass")
    return (
        col_id in {"edit-user-action", "__action__"}
        or field == "__action__"
        or value == EDIT_ACTION_LABEL
        or cell_class == "ag-action-cell"
        or (isinstance(cell_class, (list, tuple)) and "ag-action-cell" in cell_class)
    )


def register_users_callbacks(app, check_users, create_dt):
    @app.callback(
        Output("users-list-container", "children"),
        Input("main-tabs", "active_tab"),
    )
    def view_users_list(active_tab):
        if active_tab != "tab-users":
            return ""
        actor_username = str(flask_session.get("username") or "").strip()
        actor_role = str(flask_session.get("role") or "").strip()
        return _build_users_table(actor_username, actor_role, create_dt)

    @app.callback(
        [
            Output("modal-user", "is_open"),
            Output("u-modal-title", "children"),
            Output("u-form-mode", "data"),
            Output("u-edit-id", "data"),
            Output("u-username", "value"),
            Output("u-username", "disabled"),
            Output("u-full-name", "value"),
            Output("u-password", "value"),
            Output("u-role", "value"),
            Output("u-role-group", "style"),
            Output("users-alert", "children"),
            Output("users-list-container", "children", allow_duplicate=True),
        ],
        [
            Input("btn-add-user-modal", "n_clicks"),
            Input("btn-cancel-user", "n_clicks"),
            Input("btn-save-user", "n_clicks"),
            Input({"type": "edit-user", "index": ALL}, "n_clicks"),
            Input({"type": "grid", "index": "users-table"}, "cellClicked"),
        ],
        [
            State("main-tabs", "active_tab"),
            State("u-form-mode", "data"),
            State("u-edit-id", "data"),
            State("u-username", "value"),
            State("u-full-name", "value"),
            State("u-password", "value"),
            State("u-role", "value"),
        ],
        prevent_initial_call=True,
    )
    def manage_users(
        n_add,
        _n_cancel,
        n_save,
        _mobile_edit_clicks,
        grid_cell_clicked,
        active_tab,
        form_mode,
        edit_id,
        username,
        full_name,
        password,
        role,
    ):
        actor_username = str(flask_session.get("username") or "").strip()
        actor_role = str(flask_session.get("role") or "").strip() or "user"
        trigger = ctx.triggered_id

        if active_tab != "tab-users" or not actor_username:
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        if trigger == "btn-add-user-modal" and n_add:
            if not _is_admin(actor_role):
                return (
                    False,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    dbc.Alert("غير مصرح لك بإضافة مستخدمين.", color="danger"),
                    no_update,
                )
            return (
                True,
                "إضافة مستخدم جديد",
                "add",
                None,
                "",
                False,
                "",
                "",
                "user",
                _role_group_style(actor_role, "add"),
                "",
                no_update,
            )

        if trigger == "btn-cancel-user":
            reset_mode = "add"
            return (
                False,
                "إضافة مستخدم جديد",
                reset_mode,
                None,
                "",
                _username_disabled(actor_role, reset_mode),
                "",
                "",
                "user" if _is_admin(actor_role) else actor_role,
                _role_group_style(actor_role, reset_mode),
                "",
                no_update,
            )

        if isinstance(trigger, dict) and (
            (trigger.get("type") == "grid" and trigger.get("index") == "users-table")
            or trigger.get("type") == "edit-user"
        ):
            if not _is_edit_action_click(grid_cell_clicked):
                if trigger.get("type") != "edit-user":
                    return (
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                    )

            row_id = None
            if trigger.get("type") == "edit-user":
                row_id = trigger.get("index")
            elif isinstance(grid_cell_clicked, dict):
                row_id = grid_cell_clicked.get("rowId")
                if not row_id:
                    data = grid_cell_clicked.get("data") or {}
                    row_id = data.get("username")

            visible_df = logic.list_visible_users(actor_username, actor_role)
            match = visible_df[visible_df["username"].astype(str) == str(row_id)] if row_id else visible_df.iloc[0:0]
            if match.empty:
                return (
                    False,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    dbc.Alert("لا يمكنك تعديل هذا المستخدم.", color="danger"),
                    no_update,
                )

            row = match.iloc[0]
            mode = "edit_admin" if _is_admin(actor_role) else "edit_self"
            return (
                True,
                f"تعديل مستخدم: {row['username']}" if _is_admin(actor_role) else "تعديل بيانات الحساب",
                mode,
                row["username"],
                row["username"],
                _username_disabled(actor_role, mode),
                row["full_name"],
                "",
                row["role"],
                _role_group_style(actor_role, mode),
                "",
                no_update,
            )

        if trigger == "btn-save-user" and n_save:
            form_mode = str(form_mode or "add").strip() or "add"
            if form_mode == "add":
                if not _is_admin(actor_role):
                    return (
                        True,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        dbc.Alert("غير مصرح لك بإضافة مستخدمين.", color="danger"),
                        no_update,
                    )
                success, msg = logic.create_user(username, full_name, password, role)
                if success:
                    return (
                        False,
                        "إضافة مستخدم جديد",
                        "add",
                        None,
                        "",
                        False,
                        "",
                        "",
                        "user",
                        _role_group_style(actor_role, "add"),
                        dbc.Alert(msg, color="success"),
                        _build_users_table(actor_username, actor_role, create_dt),
                    )
                return (
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    dbc.Alert(msg, color="danger"),
                    no_update,
                )

            if form_mode == "edit_admin":
                success, msg, updated_username = logic.admin_update_user(edit_id, username, full_name, role, password)
                if success:
                    refreshed_actor_username = actor_username
                    refreshed_actor_role = actor_role
                    if actor_username == edit_id:
                        refreshed_actor_username = updated_username or actor_username
                        refreshed_actor_role = str(role or actor_role).strip() or actor_role
                        flask_session["username"] = refreshed_actor_username
                        flask_session["full_name"] = str(full_name or "").strip()
                        flask_session["role"] = refreshed_actor_role
                    return (
                        False,
                        "إضافة مستخدم جديد",
                        "add",
                        None,
                        "",
                        _username_disabled(refreshed_actor_role, "add"),
                        "",
                        "",
                        "user" if _is_admin(refreshed_actor_role) else refreshed_actor_role,
                        _role_group_style(refreshed_actor_role, "add"),
                        dbc.Alert(msg, color="success"),
                        _build_users_table(refreshed_actor_username, refreshed_actor_role, create_dt),
                    )
                return (
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    dbc.Alert(msg, color="danger"),
                    no_update,
                )

            success, msg, _updated_username = logic.update_own_profile(actor_username, full_name, password)
            if success:
                flask_session["full_name"] = str(full_name or "").strip()
                return (
                    False,
                    "تعديل بيانات الحساب",
                    "edit_self",
                    None,
                    actor_username,
                    True,
                    "",
                    "",
                    actor_role,
                    _role_group_style(actor_role, "edit_self"),
                    dbc.Alert(msg, color="success"),
                    _build_users_table(actor_username, actor_role, create_dt),
                )
            return (
                True,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                dbc.Alert(msg, color="danger"),
                no_update,
            )

        return (
            False,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )
