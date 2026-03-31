from dash import Input, Output, State


def _normalize_version(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def _records_from_dataframe(df):
    if df is None or getattr(df, "empty", True):
        return []
    return df.to_dict("records")


def _resolve_store_update(records, current_records, current_version):
    normalized_current = current_records if isinstance(current_records, list) else None
    version = _normalize_version(current_version)
    if normalized_current == records:
        return (normalized_current if normalized_current is not None else records), version
    return records, version + 1


def _rows(records):
    return records if isinstance(records, list) else []


def _text(value):
    return str(value or "").strip()


def _build_record_map(rows, key_field):
    record_map = {}
    for row in _rows(rows):
        key = _text(row.get(key_field))
        if not key:
            continue
        record_map[key] = row
    return record_map


def _build_customer_search_options(rows, c_cols):
    customer_id_col = c_cols[0]
    bride_name_col = c_cols[2]
    phone1_col = c_cols[5]
    return [
        {
            "label": f"{row.get(bride_name_col, '')} ({row.get(phone1_col, '')})",
            "value": row.get(customer_id_col),
        }
        for row in _rows(rows)
        if row.get(customer_id_col) is not None
    ]


def _build_service_search_options(rows, s_cols):
    service_id_col = s_cols[0]
    service_name_col = s_cols[2] if len(s_cols) > 2 else service_id_col
    return [
        {
            "label": f"{row.get(service_name_col, '')} ({row.get(service_id_col, '')})",
            "value": row.get(service_id_col),
        }
        for row in _rows(rows)
        if row.get(service_id_col) is not None
    ]


def _build_booking_search_options(rows, b_cols):
    booking_id_col = b_cols[0]
    customer_col = b_cols[2] if len(b_cols) > 2 else booking_id_col
    service_col = b_cols[4] if len(b_cols) > 4 else booking_id_col
    status_col = b_cols[11] if len(b_cols) > 11 else None
    options = []
    for row in _rows(rows):
        booking_id = row.get(booking_id_col)
        if booking_id is None:
            continue
        label = f"{row.get(customer_col, '')} ({booking_id}) - {row.get(service_col, '')}"
        if status_col is not None:
            label = f"{label} [{row.get(status_col, '')}]"
        options.append({"label": label, "value": booking_id})
    return options


def _build_payment_search_options(rows, p_cols):
    payment_id_col = p_cols[0]
    customer_name_col = p_cols[4] if len(p_cols) > 4 else payment_id_col
    return [
        {
            "label": f"{row.get(payment_id_col, '')} - {row.get(customer_name_col, '')} ({row.get(payment_id_col, '')})",
            "value": row.get(payment_id_col),
        }
        for row in _rows(rows)
        if row.get(payment_id_col) is not None
    ]


def _build_dress_search_options(rows, d_cols):
    dress_code_col = d_cols[0]
    dress_desc_col = d_cols[3] if len(d_cols) > 3 else dress_code_col
    return [
        {
            "label": f"{row.get(dress_code_col, '')} ({row.get(dress_desc_col, '')})",
            "value": row.get(dress_code_col),
        }
        for row in _rows(rows)
        if row.get(dress_code_col) is not None
    ]


def _build_department_search_options(rows):
    options = []
    seen = set()
    for row in _rows(rows):
        name = _text(row.get("department_name"))
        if not name or name in seen:
            continue
        seen.add(name)
        options.append({"label": name, "value": name})
    return options


def register_data_store_callbacks(
    app,
    load_data,
    check_departments,
    c_cols,
    s_cols,
    d_cols,
    b_cols,
    p_cols,
    dc_cols,
):
    def register_store_sync(*, data_store_id, version_store_id, inputs, loader, prevent_initial_call=False):
        @app.callback(
            [Output(data_store_id, "data"), Output(version_store_id, "data")],
            inputs,
            [State(data_store_id, "data"), State(version_store_id, "data")],
            prevent_initial_call=prevent_initial_call,
        )
        def sync_store(*args):
            current_records = args[-2]
            current_version = args[-1]
            records = _records_from_dataframe(loader())
            return _resolve_store_update(records, current_records, current_version)

    register_store_sync(
        data_store_id="customers_data",
        version_store_id="customers_version",
        inputs=[Input("post-login-prefetch", "n_intervals"), Input("customers-table-container", "children")],
        loader=lambda: load_data("customers.csv", c_cols),
    )
    register_store_sync(
        data_store_id="services_data",
        version_store_id="services_version",
        inputs=[Input("post-login-prefetch", "n_intervals"), Input("services-table-container", "children")],
        loader=lambda: load_data("services.csv", s_cols),
    )
    register_store_sync(
        data_store_id="dresses_data",
        version_store_id="dresses_version",
        inputs=[
            Input("post-login-prefetch", "n_intervals"),
            Input("dresses-table-container", "children"),
            Input("bookings-table-container", "children"),
        ],
        loader=lambda: load_data("dresses.csv", d_cols),
    )
    register_store_sync(
        data_store_id="bookings_data",
        version_store_id="bookings_version",
        inputs=[
            Input("post-login-prefetch", "n_intervals"),
            Input("bookings-table-container", "children"),
            Input("payments-table-container", "children"),
        ],
        loader=lambda: load_data("bookings.csv", b_cols),
    )
    register_store_sync(
        data_store_id="payments_data",
        version_store_id="payments_version",
        inputs=[
            Input("post-login-prefetch", "n_intervals"),
            Input("payments-table-container", "children"),
            Input("dress-custody-table-container", "children"),
        ],
        loader=lambda: load_data("payments.csv", p_cols),
    )
    register_store_sync(
        data_store_id="departments_data",
        version_store_id="departments_version",
        inputs=[Input("post-login-prefetch", "n_intervals"), Input("dept-table-container", "children")],
        loader=check_departments,
    )
    register_store_sync(
        data_store_id="dress_custody_data",
        version_store_id="dress_custody_version",
        inputs=Input("dress-custody-table-container", "children"),
        loader=lambda: load_data("dress_custody.csv", dc_cols),
        prevent_initial_call=True,
    )

    @app.callback(
        [Output("customers_search_options", "data"), Output("customers_by_id", "data")],
        [Input("customers_data", "data"), Input("customers_version", "data")],
    )
    def derive_customer_store_views(customers_data, _customers_version):
        rows = _rows(customers_data)
        return _build_customer_search_options(rows, c_cols), _build_record_map(rows, c_cols[0])

    @app.callback(
        Output("services_search_options", "data"),
        [Input("services_data", "data"), Input("services_version", "data")],
    )
    def derive_service_store_views(services_data, _services_version):
        return _build_service_search_options(_rows(services_data), s_cols)

    @app.callback(
        [Output("bookings_search_options", "data"), Output("bookings_by_id", "data")],
        [Input("bookings_data", "data"), Input("bookings_version", "data")],
    )
    def derive_booking_store_views(bookings_data, _bookings_version):
        rows = _rows(bookings_data)
        return _build_booking_search_options(rows, b_cols), _build_record_map(rows, b_cols[0])

    @app.callback(
        [Output("payments_search_options", "data"), Output("payments_by_id", "data")],
        [Input("payments_data", "data"), Input("payments_version", "data")],
    )
    def derive_payment_store_views(payments_data, _payments_version):
        rows = _rows(payments_data)
        return _build_payment_search_options(rows, p_cols), _build_record_map(rows, p_cols[0])

    @app.callback(
        [Output("dresses_search_options", "data"), Output("dresses_by_code", "data")],
        [Input("dresses_data", "data"), Input("dresses_version", "data")],
    )
    def derive_dress_store_views(dresses_data, _dresses_version):
        rows = _rows(dresses_data)
        return _build_dress_search_options(rows, d_cols), _build_record_map(rows, d_cols[0])

    @app.callback(
        Output("departments_search_options", "data"),
        [Input("departments_data", "data"), Input("departments_version", "data")],
    )
    def derive_department_store_views(departments_data, _departments_version):
        return _build_department_search_options(_rows(departments_data))
