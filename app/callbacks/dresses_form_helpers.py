from datetime import date

import dash_bootstrap_components as dbc
from dash import html, no_update

from app.callbacks.feedback import success_toast


def callback_result(*vals):
    if len(vals) == 13:
        return (*vals, no_update, no_update)
    if len(vals) == 15:
        return vals
    raise ValueError(f"Unexpected callback return length: {len(vals)}")


def idle_result():
    return callback_result(
        False,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        False,
        no_update,
        no_update,
        no_update,
    )


def build_upload_preview(upload_contents, upload_filename):
    is_image = isinstance(upload_contents, str) and upload_contents.startswith("data:image/")
    if is_image:
        return html.Div(
            [
                html.Div(f"تم تحديد: {upload_filename}", className="mb-1"),
                html.Img(
                    src=upload_contents,
                    style={
                        "maxWidth": "220px",
                        "maxHeight": "220px",
                        "borderRadius": "8px",
                        "objectFit": "cover",
                    },
                ),
            ]
        )
    return f"تم تحديد: {upload_filename}"


def upload_feedback_result(upload_contents, upload_filename):
    return callback_result(
        True,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        build_upload_preview(upload_contents, upload_filename),
        no_update,
        False,
        "",
        no_update,
        no_update,
    )


def extract_login_ts(session_data):
    if not isinstance(session_data, dict):
        return 0.0
    try:
        return float(session_data.get("login_ts") or 0)
    except Exception:
        return 0.0


def extract_trigger_ts(ctx_id, ts_map):
    try:
        return float(ts_map.get(ctx_id) or 0)
    except Exception:
        return 0.0


def add_modal_result():
    return callback_result(
        True,
        "إضافة فستان جديد",
        "",
        "زفاف",
        date.today().isoformat(),
        "متاح",
        "",
        "",
        None,
        False,
        "",
        no_update,
        no_update,
    )


def edit_modal_result(row, search_val):
    current_img = row.get("صورة الفستان", "")
    img_msg = f"الصورة الحالية: {current_img}" if current_img else "لا توجد صورة"
    return callback_result(
        True,
        f"تعديل فستان: {row['كود الفستان']}",
        row["كود الفستان"],
        row["نوع الفستان"],
        row["تاريخ الشراء"],
        row["حالة الفستان"],
        row["وصف الفستان"],
        img_msg,
        search_val,
        False,
        "",
        no_update,
        no_update,
    )


def missing_required_result():
    return callback_result(
        True,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        False,
        dbc.Alert("الكود والوصف مطلوبان", color="warning"),
        no_update,
        no_update,
    )


def save_success_result(msg, viewport_mode, get_dresses_table_content):
    return callback_result(
        False,
        no_update,
        "",
        "زفاف",
        date.today().isoformat(),
        "متاح",
        "",
        "",
        None,
        False,
        "",
        get_dresses_table_content(viewport_mode=viewport_mode),
        None,
        *success_toast(f"✅ {msg}"),
    )


def save_error_result(msg):
    return callback_result(
        True,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        False,
        dbc.Alert(f"❌ {msg}", color="danger"),
        no_update,
        no_update,
    )


def open_delete_result():
    return callback_result(
        False,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        True,
        "",
        no_update,
        no_update,
    )


def confirm_delete_success_result(viewport_mode, get_dresses_table_content):
    return callback_result(
        False,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        False,
        "",
        get_dresses_table_content(viewport_mode=viewport_mode),
        None,
        *success_toast("✅ تم حذف الفستان بنجاح"),
    )


def confirm_delete_error_result(msg, delete_reason, viewport_mode, get_dresses_table_content):
    alert = dbc.Alert(
        f"❌ لا يمكن حذف الفستان: {delete_reason(msg)}",
        color="danger",
    )
    return callback_result(
        False,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        False,
        "",
        html.Div([alert, get_dresses_table_content(viewport_mode=viewport_mode)]),
        no_update,
    )


def confirm_delete_missing_result(viewport_mode, get_dresses_table_content):
    warning_alert = dbc.Alert("اختر فستانًا قبل الحذف", color="warning")
    return callback_result(
        False,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        False,
        "",
        html.Div([warning_alert, get_dresses_table_content(viewport_mode=viewport_mode)]),
        no_update,
    )


def cancel_delete_result():
    return callback_result(
        False,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        False,
        "",
        no_update,
        no_update,
    )


def default_result(is_open, is_del_open):
    return callback_result(
        is_open,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        is_del_open,
        no_update,
        no_update,
        no_update,
    )
