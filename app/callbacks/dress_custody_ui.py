from datetime import date

from dash import Input, Output, html, no_update

from app.callbacks.dress_custody_helpers import (
    _build_alert,
    _build_custody_search_options,
    _dress_label,
    _find_custody_row,
    _modal_meta,
    _next_custody_action_label,
    _normalize_workflow_state,
    _section_style,
)


def register_dress_custody_ui_callbacks(app, load_data, dc_cols, logic_module):
    @app.callback(
        Output("dc-search", "options"),
        [Input("dress-custody-table-container", "children"), Input("main-tabs", "active_tab"), Input("dc-stage-filter", "value")],
    )
    def update_custody_search_options(_table, active_tab, stage_filter):
        if active_tab != "tab-dress-custody":
            return no_update
        return _build_custody_search_options(load_data, dc_cols, stage_filter)

    @app.callback(Output("dc-return-compensation-wrap", "style"), Input("dc-return-damage", "value"))
    def toggle_return_compensation_wrap(damage_value):
        return {"display": "block"} if damage_value == "damage" else {"display": "none"}

    @app.callback(Output("dc-summary", "children"), Input("dc-workflow-state", "data"))
    def refresh_custody_summary(workflow_state):
        custody_id = _normalize_workflow_state(workflow_state).get("selected_custody_id")
        row, _ = _find_custody_row(load_data, dc_cols, custody_id)
        if row is None:
            return "اختر سجلًا لعرض التفاصيل."
        status = str(row.get("حالة الدورة", "")).strip()
        deposit = float(row.get("قيمة التأمين", 0) or 0)
        refunded = float(row.get("التأمين المردود", 0) or 0)
        used = float(row.get("التأمين المعتمد للتعويض", 0) or 0)
        extra_collected = float(row.get("تعويض إضافي محصل", 0) or 0)
        service_status = str(row.get("حالة المغسلة والصيانة", "") or "").strip()
        guarantee_type = row.get("نوع الضمان", "-")
        guarantee_reference = row.get("مرجع الضمان", "-")
        return html.Div(
            [
                html.Div(f"الحالة الحالية: {status}", className="fw-bold mb-2"),
                html.Div(_next_custody_action_label(row, logic_module), className="text-muted mb-2"),
                html.Div(f"الحجز: {row.get('كود الحجز', '-')}"),
                html.Div(f"العميلة: {row.get('اسم العروسه', '-')}"),
                html.Div(f"الفستان / العهدة: {_dress_label(row.get('كود الفستان', ''))}"),
                html.Div(f"حالة المغسلة والصيانة: {service_status or '-'}"),
                html.Div(f"التأمين: {deposit:,.2f}"),
                html.Div(f"المردود من التأمين: {refunded:,.2f}"),
                html.Div(f"المعتمد للتعويض: {used:,.2f}"),
                html.Div(f"إجمالي التعويض المحصل: {used + extra_collected:,.2f}"),
                html.Div(f"الضمان: {guarantee_type}", className="mt-2"),
                html.Div(f"مرجع الضمان: {guarantee_reference}"),
            ]
        )

    @app.callback(
        [
            Output("modal-custody-workflow", "is_open"),
            Output("dc-workflow-title", "children"),
            Output("btn-save-custody-workflow", "children"),
            Output("btn-save-custody-workflow", "color"),
            Output("dc-create-section", "style"),
            Output("dc-action-section", "style"),
            Output("dc-return-section", "style"),
            Output("dc-service-section", "style"),
            Output("dc-booking", "options"),
            Output("dc-booking", "value"),
            Output("dc-deposit-amount", "value"),
            Output("dc-guarantee-type", "value"),
            Output("dc-guarantee-reference", "value"),
            Output("dc-create-notes", "value"),
            Output("dc-action-date", "value"),
            Output("dc-action-condition", "value"),
            Output("dc-action-notes", "value"),
            Output("dc-return-date", "value"),
            Output("dc-return-condition", "value"),
            Output("dc-return-damage", "value"),
            Output("dc-return-compensation", "value"),
            Output("dc-return-guarantee", "value"),
            Output("dc-return-guarantee-date", "value"),
            Output("dc-return-notes", "value"),
            Output("dc-service-date", "value"),
            Output("dc-service-status", "value"),
            Output("dc-service-notes", "value"),
            Output("dc-workflow-alert", "children"),
        ],
        Input("dc-workflow-state", "data"),
    )
    def render_workflow_modal(workflow_state):
        state = _normalize_workflow_state(workflow_state)
        kind = state.get("modal_kind")
        prefill = state.get("prefill_data") or {}
        title, save_label, save_color = _modal_meta(kind)
        today_value = date.today().isoformat()
        return (
            bool(state.get("modal_open")),
            title,
            save_label,
            save_color,
            _section_style(kind, "create"),
            _section_style(kind, "handover"),
            _section_style(kind, "return"),
            _section_style(kind, "service"),
            prefill.get("booking_options", []),
            prefill.get("booking_id"),
            prefill.get("deposit_amount", 0),
            prefill.get("guarantee_type", ""),
            prefill.get("guarantee_reference", ""),
            prefill.get("create_notes", ""),
            prefill.get("action_date", today_value),
            prefill.get("action_condition", ""),
            prefill.get("action_notes", ""),
            prefill.get("return_date", today_value),
            prefill.get("return_condition", ""),
            prefill.get("return_damage", "clean"),
            prefill.get("return_compensation", 0),
            prefill.get("return_guarantee", ["returned"]),
            prefill.get("return_guarantee_date", today_value),
            prefill.get("return_notes", ""),
            prefill.get("service_date", today_value),
            prefill.get("service_status", logic_module.DRESS_CUSTODY_SERVICE_STATUS_LAUNDRY),
            prefill.get("service_notes", ""),
            _build_alert(state.get("alert")),
        )
