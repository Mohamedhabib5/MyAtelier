from datetime import date

from dash import ALL, Input, Output, State, ctx, no_update

from app.callbacks.dress_custody_helpers import (
    _build_create_prefill,
    _current_prefill_for_kind,
    _empty_workflow_state,
    _find_custody_row,
    _is_action_click,
    _is_recent_mobile_trigger,
    _normalize_workflow_state,
    _open_state_for_row,
    _with_workflow_state,
    _workflow_alert,
)
from app.callbacks.feedback import success_toast


def register_dress_custody_state_callbacks(app, load_data, b_cols, dc_cols, get_dress_custody_table_content, logic_module):
    @app.callback(
        [
            Output("dc-workflow-state", "data"),
            Output("dress-custody-table-container", "children"),
            Output("dc-stage-filter", "value"),
            Output("app-success-toast", "children", allow_duplicate=True),
            Output("app-success-toast", "is_open", allow_duplicate=True),
        ],
        [
            Input("main-tabs", "active_tab"),
            Input("dc-search", "value"),
            Input({"type": "grid", "index": "dress-custody-table"}, "cellClicked"),
            Input("btn-open-custody-modal", "n_clicks"),
            Input({"type": "custody-next-action", "index": ALL}, "n_clicks_timestamp"),
            Input("btn-close-custody-workflow", "n_clicks"),
            Input("btn-save-custody-workflow", "n_clicks"),
        ],
        [
            State("dc-workflow-state", "data"),
            State("dc-booking", "value"),
            State("dc-deposit-amount", "value"),
            State("dc-guarantee-type", "value"),
            State("dc-guarantee-reference", "value"),
            State("dc-create-notes", "value"),
            State("dc-action-date", "value"),
            State("dc-action-condition", "value"),
            State("dc-action-notes", "value"),
            State("dc-return-date", "value"),
            State("dc-return-condition", "value"),
            State("dc-return-damage", "value"),
            State("dc-return-compensation", "value"),
            State("dc-return-guarantee", "value"),
            State("dc-return-guarantee-date", "value"),
            State("dc-return-notes", "value"),
            State("dc-service-date", "value"),
            State("dc-service-status", "value"),
            State("dc-service-notes", "value"),
            State("user_session_store", "data"),
            State("dc-stage-filter", "value"),
            State("viewport-mode", "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_workflow_state(
        active_tab,
        search_value,
        grid_click,
        n_open,
        mobile_clicks,
        n_close,
        n_save,
        workflow_state,
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
        session_data,
        current_stage_filter,
        viewport_mode,
    ):
        state = _normalize_workflow_state(workflow_state)
        ctx_id = ctx.triggered_id
        empty_toast = (no_update, no_update)

        if ctx_id == "main-tabs":
            if active_tab != "tab-dress-custody":
                return _empty_workflow_state(), no_update, no_update, *empty_toast
            return _empty_workflow_state(), no_update, current_stage_filter or "customer", *empty_toast

        if active_tab != "tab-dress-custody":
            return _empty_workflow_state(), no_update, no_update, *empty_toast

        if ctx_id == "dc-search":
            if search_value == state.get("selected_custody_id") and not state.get("modal_open") and not state.get("alert"):
                return no_update, no_update, no_update, *empty_toast
            return _empty_workflow_state(selected_custody_id=search_value), no_update, no_update, *empty_toast

        if isinstance(ctx_id, dict) and ctx_id.get("type") == "grid":
            row_id = (grid_click or {}).get("rowId") or ((grid_click or {}).get("data") or {}).get("كود السجل")
            if not row_id:
                return no_update, no_update, no_update, *empty_toast
            if not _is_action_click(grid_click):
                return _empty_workflow_state(selected_custody_id=row_id), no_update, no_update, *empty_toast
            return _open_state_for_row(row_id, state, load_data, dc_cols, logic_module), no_update, no_update, *empty_toast

        if isinstance(ctx_id, dict) and ctx_id.get("type") == "custody-next-action":
            if not _is_recent_mobile_trigger(session_data):
                return no_update, no_update, no_update, *empty_toast
            return _open_state_for_row(ctx_id.get("index"), state, load_data, dc_cols, logic_module), no_update, no_update, *empty_toast

        if ctx_id == "btn-open-custody-modal":
            if not n_open:
                return no_update, no_update, no_update, *empty_toast
            return (
                _with_workflow_state(
                    state,
                    modal_kind="create",
                    modal_open=True,
                    prefill_data=_build_create_prefill(load_data, b_cols),
                    alert=None,
                ),
                no_update,
                no_update,
                *empty_toast,
            )

        if ctx_id == "btn-close-custody-workflow":
            if not n_close:
                return no_update, no_update, no_update, *empty_toast
            return _empty_workflow_state(selected_custody_id=state.get("selected_custody_id")), no_update, no_update, *empty_toast

        if ctx_id != "btn-save-custody-workflow" or not n_save:
            return no_update, no_update, no_update, *empty_toast

        kind = state.get("modal_kind")
        custody_id = state.get("selected_custody_id")
        full_name = ""
        if isinstance(session_data, dict):
            full_name = session_data.get("full_name") or session_data.get("username") or ""

        current_prefill = _current_prefill_for_kind(
            kind,
            booking_options=(state.get("prefill_data") or {}).get("booking_options"),
            booking_id=booking_id,
            deposit_amount=deposit_amount,
            guarantee_type=guarantee_type,
            guarantee_reference=guarantee_reference,
            create_notes=create_notes,
            action_date=action_date,
            action_condition=action_condition,
            action_notes=action_notes,
            return_date=return_date,
            return_condition=return_condition,
            damage_mode=damage_mode,
            compensation_amount=compensation_amount,
            guarantee_value=guarantee_value,
            guarantee_date=guarantee_date,
            return_notes=return_notes,
            service_date=service_date,
            service_status=service_status,
            service_notes=service_notes,
        )

        if kind == "create":
            success, msg, new_custody_id = logic_module.create_dress_custody(
                booking_id,
                deposit_amount,
                guarantee_type=guarantee_type,
                guarantee_reference=guarantee_reference,
                notes=create_notes,
                handled_by=full_name,
                created_date=date.today().isoformat(),
            )
            if success:
                return (
                    _empty_workflow_state(selected_custody_id=new_custody_id),
                    get_dress_custody_table_content(viewport_mode=viewport_mode),
                    "customer",
                    *success_toast("تم فتح سجل التسليم والاستلام"),
                )
            return (
                _with_workflow_state(state, modal_kind="create", modal_open=True, prefill_data=current_prefill, alert=_workflow_alert(msg)),
                no_update,
                no_update,
                *empty_toast,
            )

        if kind == "handover":
            success, msg = logic_module.handover_dress_custody(
                custody_id,
                handover_date=action_date,
                condition_out=action_condition,
                notes=action_notes,
                handled_by=full_name,
            )
            if success:
                return (
                    _empty_workflow_state(selected_custody_id=custody_id),
                    get_dress_custody_table_content(viewport_mode=viewport_mode),
                    "customer",
                    *success_toast(msg),
                )
            return (
                _with_workflow_state(state, modal_kind="handover", modal_open=True, prefill_data=current_prefill, alert=_workflow_alert(msg)),
                no_update,
                no_update,
                *empty_toast,
            )

        if kind == "return":
            success, msg = logic_module.receive_dress_from_customer(
                custody_id,
                return_date=return_date,
                condition_in=return_condition,
                damage_notes=return_notes,
                handled_by=full_name,
                has_damage=damage_mode == "damage",
                compensation_amount=compensation_amount if damage_mode == "damage" else 0,
                guarantee_returned="returned" in (guarantee_value or []),
                guarantee_return_date=guarantee_date,
            )
            if success:
                row, _ = _find_custody_row(load_data, dc_cols, custody_id)
                next_filter = "service" if row is not None and str(row.get("كود الفستان", "")).strip() else "closed"
                return (
                    _empty_workflow_state(selected_custody_id=custody_id),
                    get_dress_custody_table_content(viewport_mode=viewport_mode),
                    next_filter,
                    *success_toast(msg),
                )
            return (
                _with_workflow_state(state, modal_kind="return", modal_open=True, prefill_data=current_prefill, alert=_workflow_alert(msg)),
                no_update,
                no_update,
                *empty_toast,
            )

        if kind == "service":
            success, msg = logic_module.update_dress_custody_service_status(
                custody_id,
                service_status,
                action_date=service_date,
                notes=service_notes,
                handled_by=full_name,
            )
            if success:
                next_filter = "closed" if service_status == logic_module.DRESS_CUSTODY_SERVICE_STATUS_AVAILABLE else "service"
                return (
                    _empty_workflow_state(selected_custody_id=custody_id),
                    get_dress_custody_table_content(viewport_mode=viewport_mode),
                    next_filter,
                    *success_toast(msg),
                )
            return (
                _with_workflow_state(state, modal_kind="service", modal_open=True, prefill_data=current_prefill, alert=_workflow_alert(msg)),
                no_update,
                no_update,
                *empty_toast,
            )

        return (
            _with_workflow_state(state, alert=_workflow_alert("لا توجد عملية مفتوحة حاليًا.", color="warning")),
            no_update,
            no_update,
            *empty_toast,
        )
