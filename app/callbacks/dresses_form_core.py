from app.callbacks.dresses_form_helpers import (
    add_modal_result,
    cancel_delete_result,
    confirm_delete_error_result,
    confirm_delete_missing_result,
    confirm_delete_success_result,
    default_result,
    edit_modal_result,
    extract_login_ts,
    extract_trigger_ts,
    idle_result,
    missing_required_result,
    open_delete_result,
    save_error_result,
    save_success_result,
    upload_feedback_result,
)


def manage_dresses_request(
    *,
    ctx_id,
    triggered_val,
    upload_contents,
    is_open,
    search_val,
    is_del_open,
    active_tab,
    ts_map,
    session_data,
    viewport_mode,
    code,
    dtype,
    buy_date,
    status,
    desc,
    edit_id,
    upload_filename,
    load_data,
    d_cols,
    get_dresses_table_content,
    logic_module,
    delete_reason,
):
    if ctx_id == "d-upload-image" and upload_filename:
        return upload_feedback_result(upload_contents, upload_filename)

    if not isinstance(triggered_val, (int, float)) or triggered_val <= 0:
        return idle_result()

    login_ts = extract_login_ts(session_data)
    trigger_ts = extract_trigger_ts(ctx_id, ts_map)
    if ctx_id in ts_map and login_ts > 0 and trigger_ts > 0 and trigger_ts < login_ts:
        return idle_result()

    if ctx_id == "btn-add-dress-modal" and active_tab == "tab-dresses":
        return add_modal_result()

    if ctx_id == "btn-edit-dress" and active_tab == "tab-dresses" and search_val:
        df = load_data("dresses.csv", d_cols)
        row = df[df["كود الفستان"] == search_val]
        if not row.empty:
            return edit_modal_result(row.iloc[0], search_val)

    if ctx_id == "btn-save-dress" and active_tab == "tab-dresses":
        if not code or not desc:
            return missing_required_result()
        if edit_id:
            success, msg = logic_module.update_dress(edit_id, code, dtype, buy_date, status, desc, upload_contents)
        else:
            success, msg = logic_module.add_dress(code, dtype, buy_date, status, desc, upload_contents)
        if success:
            return save_success_result(msg, viewport_mode, get_dresses_table_content)
        return save_error_result(msg)

    if ctx_id == "btn-delete-dress" and active_tab == "tab-dresses":
        return open_delete_result()

    if ctx_id == "btn-confirm-delete-d" and active_tab == "tab-dresses":
        if search_val:
            ok, msg = logic_module.delete_dress(search_val)
            if ok:
                return confirm_delete_success_result(viewport_mode, get_dresses_table_content)
            return confirm_delete_error_result(msg, delete_reason, viewport_mode, get_dresses_table_content)
        return confirm_delete_missing_result(viewport_mode, get_dresses_table_content)

    if ctx_id == "btn-cancel-delete-d" and active_tab == "tab-dresses":
        return cancel_delete_result()

    return default_result(is_open, is_del_open)
