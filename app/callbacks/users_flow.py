from flask import session as flask_session

import dash_bootstrap_components as dbc
from dash import no_update

import logic
from app.callbacks.users_shared import (
    build_users_table,
    is_admin,
    is_edit_action_click,
    role_group_style,
    username_disabled,
)


def hidden_result():
    return (False,) + (no_update,) * 11


def add_user_result(actor_role):
    if not is_admin(actor_role):
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
        role_group_style(actor_role, "add"),
        "",
        no_update,
    )


def cancel_user_result(actor_role):
    reset_mode = "add"
    return (
        False,
        "إضافة مستخدم جديد",
        reset_mode,
        None,
        "",
        username_disabled(actor_role, reset_mode),
        "",
        "",
        "user" if is_admin(actor_role) else actor_role,
        role_group_style(actor_role, reset_mode),
        "",
        no_update,
    )


def _resolve_edit_username(trigger, grid_cell_clicked):
    if isinstance(trigger, dict) and trigger.get("type") == "edit-user":
        return trigger.get("index")
    if isinstance(grid_cell_clicked, dict):
        row_id = grid_cell_clicked.get("rowId")
        if row_id:
            return row_id
        data = grid_cell_clicked.get("data") or {}
        return data.get("username")
    return None


def edit_user_result(trigger, grid_cell_clicked, actor_username, actor_role):
    if isinstance(trigger, dict) and trigger.get("type") == "grid" and trigger.get("index") == "users-table":
        if not is_edit_action_click(grid_cell_clicked):
            return hidden_result()

    row_id = _resolve_edit_username(trigger, grid_cell_clicked)
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
    mode = "edit_admin" if is_admin(actor_role) else "edit_self"
    return (
        True,
        f"تعديل مستخدم: {row['username']}" if is_admin(actor_role) else "تعديل بيانات الحساب",
        mode,
        row["username"],
        row["username"],
        username_disabled(actor_role, mode),
        row["full_name"],
        "",
        row["role"],
        role_group_style(actor_role, mode),
        "",
        no_update,
    )


def save_user_result(
    *,
    actor_username,
    actor_role,
    viewport_mode,
    form_mode,
    edit_id,
    username,
    full_name,
    password,
    role,
    create_dt,
):
    form_mode = str(form_mode or "add").strip() or "add"
    if form_mode == "add":
        if not is_admin(actor_role):
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
                role_group_style(actor_role, "add"),
                dbc.Alert(msg, color="success"),
                build_users_table(actor_username, actor_role, create_dt, viewport_mode=viewport_mode),
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
                username_disabled(refreshed_actor_role, "add"),
                "",
                "",
                "user" if is_admin(refreshed_actor_role) else refreshed_actor_role,
                role_group_style(refreshed_actor_role, "add"),
                dbc.Alert(msg, color="success"),
                build_users_table(refreshed_actor_username, refreshed_actor_role, create_dt, viewport_mode=viewport_mode),
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
            role_group_style(actor_role, "edit_self"),
            dbc.Alert(msg, color="success"),
            build_users_table(actor_username, actor_role, create_dt, viewport_mode=viewport_mode),
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
