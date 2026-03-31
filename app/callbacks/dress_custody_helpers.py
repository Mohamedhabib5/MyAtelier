from datetime import date

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, ctx, html, no_update

from app.callbacks.feedback import success_toast
from app.table_content.dress_custody import NEXT_ACTION_LABEL


EMPTY_WORKFLOW_STATE = {
    "selected_custody_id": None,
    "modal_kind": None,
    "modal_open": False,
    "prefill_data": {},
    "alert": None,
}


def _empty_workflow_state(selected_custody_id=None):
    state = dict(EMPTY_WORKFLOW_STATE)
    state["selected_custody_id"] = selected_custody_id
    return state


def _normalize_workflow_state(state):
    normalized = _empty_workflow_state()
    if not isinstance(state, dict):
        return normalized

    normalized["selected_custody_id"] = state.get("selected_custody_id")
    normalized["modal_kind"] = state.get("modal_kind")
    normalized["modal_open"] = bool(state.get("modal_open"))
    normalized["prefill_data"] = state.get("prefill_data") if isinstance(state.get("prefill_data"), dict) else {}
    normalized["alert"] = state.get("alert") if isinstance(state.get("alert"), dict) else None
    return normalized


def _with_workflow_state(state, **updates):
    next_state = _normalize_workflow_state(state)
    next_state.update(updates)
    if not isinstance(next_state.get("prefill_data"), dict):
        next_state["prefill_data"] = {}
    if not isinstance(next_state.get("alert"), dict):
        next_state["alert"] = None
    return next_state


def _workflow_alert(message, color="danger"):
    if not message:
        return None
    return {"message": message, "color": color}


def _build_alert(alert_data):
    if not isinstance(alert_data, dict) or not alert_data.get("message"):
        return ""
    return dbc.Alert(alert_data["message"], color=alert_data.get("color", "danger"))


def _find_custody_row(load_data, dc_cols, custody_id):
    df = load_data("dress_custody.csv", dc_cols)
    if df.empty or not custody_id or dc_cols[0] not in df.columns:
        return None, df
    row = df[df[dc_cols[0]] == custody_id]
    if row.empty:
        return None, df
    return row.iloc[0], df


def _dress_label(value):
    text = str(value or "").strip()
    return text if text else "بدون فستان"


def _status_matches_filter(status, stage_filter):
    status = str(status or "").strip()
    if stage_filter == "service":
        return status == "في المغسلة والصيانة"
    if stage_filter == "closed":
        return status in {"متاح للإيجار", "مغلق"}
    return status in {"جاهز للتسليم", "عند العميل"}


def _build_open_booking_options(load_data, b_cols):
    b_df = load_data("bookings.csv", b_cols)
    dc_df = load_data("dress_custody.csv")
    used = set()
    if not dc_df.empty and "كود الحجز" in dc_df.columns:
        used = {str(v).strip() for v in dc_df["كود الحجز"].tolist() if str(v).strip()}

    options = []
    for _, row in b_df.iterrows():
        booking_id = str(row.get(b_cols[0], "")).strip()
        if not booking_id or booking_id in used:
            continue
        dress_code = str(row.get(b_cols[5], "")).strip() if len(b_cols) > 5 else ""
        customer = str(row.get(b_cols[2], "")).strip() if len(b_cols) > 2 else booking_id
        service = str(row.get(b_cols[4], "")).strip() if len(b_cols) > 4 else ""
        dress_label = dress_code if dress_code not in {"", "-", "None", "nan"} else "بدون فستان"
        options.append({"label": f"{customer} ({booking_id}) - {dress_label} - {service}", "value": booking_id})
    return options


def _build_custody_search_options(load_data, dc_cols, stage_filter):
    df = load_data("dress_custody.csv", dc_cols)
    if df.empty:
        return []
    options = []
    for _, row in df.iterrows():
        status = row.get("حالة الدورة", "")
        if not _status_matches_filter(status, stage_filter):
            continue
        booking_id = row.get("كود الحجز", "")
        customer = row.get("اسم العروسه", "")
        dress = _dress_label(row.get("كود الفستان", ""))
        options.append(
            {
                "label": f"{customer} ({booking_id}) - {dress} - {status}",
                "value": row.get("كود السجل", ""),
            }
        )
    return options


def _next_custody_action_label(row, logic_module):
    status = str(row.get("حالة الدورة", "")).strip()
    service_status = str(row.get("حالة المغسلة والصيانة", "")).strip()
    if status == logic_module.DRESS_CUSTODY_STATUS_READY:
        return "الإجراء التالي: تسليم للعميل"
    if status == logic_module.DRESS_CUSTODY_STATUS_HANDED_OVER:
        return "الإجراء التالي: استلام من العميل"
    if status == logic_module.DRESS_CUSTODY_STATUS_IN_SERVICE:
        if service_status == logic_module.DRESS_CUSTODY_SERVICE_STATUS_MAINTENANCE:
            return "الإجراء التالي: اعتماد الفستان متاحًا للإيجار أو إبقاؤه تحت الصيانة"
        return "الإجراء التالي: تحديث مرحلة المغسلة والصيانة"
    if status == logic_module.DRESS_CUSTODY_STATUS_AVAILABLE:
        return "الإجراء التالي: لا توجد، الفستان متاح للإيجار"
    if status == logic_module.DRESS_CUSTODY_STATUS_CLOSED:
        return "الإجراء التالي: لا توجد، العملية مغلقة"
    return "الإجراء التالي: راجع حالة السجل"


def _is_action_click(cell_clicked):
    if not cell_clicked:
        return False
    col_id = cell_clicked.get("colId") or cell_clicked.get("columnId")
    col_def = cell_clicked.get("colDef") or {}
    field = cell_clicked.get("field") or col_def.get("field")
    value = str(cell_clicked.get("value") or "").strip()
    return (
        col_id in {"custody-next-action", "__action__"}
        or field == "__action__"
        or value == NEXT_ACTION_LABEL
        or col_def.get("cellClass") == "ag-action-cell"
    )


def _is_recent_mobile_trigger(session_data):
    if not isinstance(ctx.triggered_id, dict) or ctx.triggered_id.get("type") != "custody-next-action":
        return False
    try:
        triggered_value = ctx.triggered[0].get("value")
        if triggered_value in (None, "", 0):
            return False
        login_ts = int((session_data or {}).get("login_ts") or 0)
        return int(triggered_value) > login_ts
    except Exception:
        return False


def _modal_meta(kind):
    mapping = {
        "create": ("فتح سجل تسليم واستلام", "حفظ", "primary"),
        "handover": ("تسليم للعميل", "تأكيد التسليم", "primary"),
        "return": ("استلام من العميل", "اعتماد الاستلام", "warning"),
        "service": ("تحديث حالة المغسلة والصيانة", "حفظ التحديث", "secondary"),
    }
    return mapping.get(kind, ("التسليم والاستلام", "حفظ", "primary"))


def _section_style(kind, target):
    return {"display": "block"} if kind == target else {"display": "none"}


def _build_create_prefill(load_data, b_cols):
    return {
        "booking_options": _build_open_booking_options(load_data, b_cols),
        "booking_id": None,
        "deposit_amount": 0,
        "guarantee_type": "",
        "guarantee_reference": "",
        "create_notes": "",
    }


def _build_handover_prefill(row):
    return {
        "action_date": date.today().isoformat(),
        "action_condition": row.get("حالة العهدة عند التسليم", ""),
        "action_notes": "",
    }


def _build_return_prefill(row):
    deposit = float(row.get("قيمة التأمين", 0) or 0)
    return {
        "return_date": date.today().isoformat(),
        "return_condition": row.get("حالة العهدة عند الاستلام", ""),
        "return_damage": "clean",
        "return_compensation": deposit,
        "return_guarantee": ["returned"],
        "return_guarantee_date": date.today().isoformat(),
        "return_notes": "",
    }


def _build_service_prefill(row, logic_module):
    service_status = str(row.get("حالة المغسلة والصيانة", "") or "").strip() or logic_module.DRESS_CUSTODY_SERVICE_STATUS_LAUNDRY
    return {
        "service_date": date.today().isoformat(),
        "service_status": service_status,
        "service_notes": "",
    }


def _open_state_for_row(row_id, current_state, load_data, dc_cols, logic_module):
    row, _ = _find_custody_row(load_data, dc_cols, row_id)
    if row is None:
        return _empty_workflow_state(selected_custody_id=row_id)

    status = str(row.get("حالة الدورة", "")).strip()
    if status == logic_module.DRESS_CUSTODY_STATUS_READY:
        return _with_workflow_state(
            current_state,
            selected_custody_id=row_id,
            modal_kind="handover",
            modal_open=True,
            prefill_data=_build_handover_prefill(row),
            alert=None,
        )
    if status == logic_module.DRESS_CUSTODY_STATUS_HANDED_OVER:
        return _with_workflow_state(
            current_state,
            selected_custody_id=row_id,
            modal_kind="return",
            modal_open=True,
            prefill_data=_build_return_prefill(row),
            alert=None,
        )
    if status == logic_module.DRESS_CUSTODY_STATUS_IN_SERVICE:
        return _with_workflow_state(
            current_state,
            selected_custody_id=row_id,
            modal_kind="service",
            modal_open=True,
            prefill_data=_build_service_prefill(row, logic_module),
            alert=None,
        )
    return _empty_workflow_state(selected_custody_id=row_id)


def _current_prefill_for_kind(
    kind,
    *,
    booking_options,
    booking_id,
    deposit_amount,
    guarantee_type,
    guarantee_reference,
    create_notes,
    action_date,
    action_condition,
    action_notes,
    return_date,
    return_condition,
    damage_mode,
    compensation_amount,
    guarantee_value,
    guarantee_date,
    return_notes,
    service_date,
    service_status,
    service_notes,
):
    if kind == "create":
        return {
            "booking_options": booking_options or [],
            "booking_id": booking_id,
            "deposit_amount": deposit_amount,
            "guarantee_type": guarantee_type,
            "guarantee_reference": guarantee_reference,
            "create_notes": create_notes,
        }
    if kind == "handover":
        return {
            "action_date": action_date,
            "action_condition": action_condition,
            "action_notes": action_notes,
        }
    if kind == "return":
        return {
            "return_date": return_date,
            "return_condition": return_condition,
            "return_damage": damage_mode,
            "return_compensation": compensation_amount,
            "return_guarantee": guarantee_value or [],
            "return_guarantee_date": guarantee_date,
            "return_notes": return_notes,
        }
    if kind == "service":
        return {
            "service_date": service_date,
            "service_status": service_status,
            "service_notes": service_notes,
        }
    return {}


