import dash_bootstrap_components as dbc
from dash import no_update


def build_booking_manage_default_result(is_open, is_del_open):
    return (
        is_open,
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
        is_del_open,
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


def build_booking_customer_options(c_df, c_cols):
    if c_df.empty:
        return []

    bride_col = c_cols[2] if len(c_cols) > 2 else c_cols[0]
    groom_col = c_cols[3] if len(c_cols) > 3 else bride_col
    return [
        {"label": f"{r[bride_col]} | {r[groom_col]}", "value": r[bride_col]}
        for _, r in c_df.iterrows()
    ]


def build_booking_dress_options(d_df, d_cols):
    if d_df.empty:
        return []

    code_col = d_cols[0]
    desc_col = d_cols[3] if len(d_cols) > 3 else code_col
    status_col = d_cols[5] if len(d_cols) > 5 else None
    options = []
    for _, row in d_df.iterrows():
        code = row[code_col]
        if status_col is None:
            label = f"{code} | {row[desc_col]}"
        else:
            label = f"{code} | {row[desc_col]} ({row[status_col]})"
        options.append({"label": label, "value": code})
    return options


def load_booking_form_seed_data(load_data, c_cols, d_cols, s_cols):
    c_df = load_data("customers.csv", c_cols)
    d_df = load_data("dresses.csv", d_cols)
    s_df = load_data("services.csv", s_cols)
    return {
        "customers_df": c_df,
        "dresses_df": d_df,
        "services_df": s_df,
        "customer_options": build_booking_customer_options(c_df, c_cols),
        "dress_options": build_booking_dress_options(d_df, d_cols),
    }


def build_booking_service_options_for_dept(s_df, s_cols, dept):
    if not dept or s_df.empty:
        return []

    dept_col = s_cols[1] if len(s_cols) > 1 else s_cols[0]
    service_name_col = s_cols[2] if len(s_cols) > 2 else s_cols[0]
    service_price_col = s_cols[3] if len(s_cols) > 3 else None
    s_filtered = s_df[s_df[dept_col].astype(str).str.strip() == str(dept).strip()]
    options = []
    for _, row in s_filtered.iterrows():
        service_name = str(row[service_name_col]).strip()
        if not service_name:
            continue
        if service_price_col is None:
            label = service_name
        else:
            label = f"{service_name} ({row[service_price_col]})"
        options.append({"label": label, "value": service_name})
    return options


def ensure_booking_service_option(service_options, current_service):
    value = str(current_service or "").strip()
    if not value:
        return service_options
    if value in {opt["value"] for opt in service_options}:
        return service_options
    return service_options + [{"label": f"{value} (missing)", "value": value}]


def ensure_booking_dress_option(dress_options, current_dress, normalize_code):
    value = str(current_dress or "").strip()
    normalized = normalize_code(value)
    if not normalized:
        return dress_options
    existing = {normalize_code(opt["value"]) for opt in dress_options}
    if normalized in existing:
        return dress_options
    return dress_options + [{"label": f"{value} (missing)", "value": value}]


def build_booking_edit_context(
    row,
    b_cols,
    s_df,
    s_cols,
    dress_options,
    normalize_code,
    is_dresses_dept,
):
    curr_dept = row[b_cols[3]]
    service_options = build_booking_service_options_for_dept(s_df, s_cols, curr_dept)
    curr_service = row[b_cols[4]]
    curr_dress = row[b_cols[5]]
    return {
        "dept": curr_dept,
        "service_options": ensure_booking_service_option(service_options, curr_service),
        "dress_options": ensure_booking_dress_option(dress_options, curr_dress, normalize_code),
        "dress_style": {"display": "block"} if is_dresses_dept(curr_dept) else {"display": "none"},
    }


def build_booking_error_alert(msg, fallback):
    text = (msg or "").strip()
    if not text or text == "Dress Taken":
        text = fallback
    return dbc.Alert(text, color="danger")


def execute_booking_save(
    logic_module,
    edit_id,
    fit_cust,
    fit_dept,
    fit_service,
    fit_dress,
    fit_event_date,
    fit_price,
    fit_paid,
    fit_status,
    fit_notes,
    fit_book_date,
    is_dresses_dept,
):
    dress_val = fit_dress if (is_dresses_dept(fit_dept) and fit_dress) else "-"
    if edit_id:
        success, msg = logic_module.update_booking(
            edit_id,
            fit_cust,
            fit_dept,
            fit_service,
            dress_val,
            fit_event_date,
            fit_price,
            fit_paid,
            fit_status,
            fit_notes,
        )
        return {"mode": "edit", "success": success, "msg": msg}

    success, msg, _new_id = logic_module.add_booking(
        fit_cust,
        fit_dept,
        fit_service,
        dress_val,
        fit_event_date,
        fit_price,
        fit_paid,
        fit_status,
        fit_notes,
        reg_date=fit_book_date,
    )
    return {"mode": "add", "success": success, "msg": msg}
