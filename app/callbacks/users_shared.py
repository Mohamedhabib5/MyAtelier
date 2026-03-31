from flask import session as flask_session

import dash_bootstrap_components as dbc

import logic


EDIT_ACTION_LABEL = "تعديل"


def is_admin(role):
    return str(role or "").strip() == "admin"


def role_group_style(role, form_mode):
    if is_admin(role) and form_mode in {"add", "edit_admin"}:
        return {}
    return {"display": "none"}


def username_disabled(role, form_mode):
    return (not is_admin(role)) or form_mode == "edit_self"


def current_actor():
    return (
        str(flask_session.get("username") or "").strip(),
        str(flask_session.get("role") or "").strip() or "user",
    )


def build_users_table(actor_username, actor_role, create_dt, viewport_mode="responsive"):
    df = logic.list_visible_users(actor_username, actor_role)
    if df.empty:
        return dbc.Alert("لا توجد بيانات مستخدمين.", color="info")

    visible_cols = ["username", "full_name", "role", "created_date"] if is_admin(actor_role) else [
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
        viewport_mode=viewport_mode,
    )


def is_edit_action_click(cell_clicked):
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
