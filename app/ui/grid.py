from dash import html
import dash_bootstrap_components as dbc
import dash_ag_grid as dag


def _stringify_mobile_value(value):
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "none"}:
        return ""
    return text


def _guess_title_field(fields):
    preferred_tokens = (
        "اسم",
        "name",
        "الخدمة",
        "service",
        "department",
        "القسم",
        "description",
        "الوصف",
        "customer",
        "full_name",
    )
    lowered = [(field, str(field).lower()) for field in fields]
    for token in preferred_tokens:
        for field, lowered_field in lowered:
            if token.lower() in lowered_field:
                return field
    return fields[0] if fields else None


def build_mobile_record_list(
    *,
    row_data,
    row_id_field=None,
    title_field=None,
    field_order=None,
    select_target=None,
    select_label="تحديد",
    action=None,
):
    if not row_data:
        return None

    records = []
    action = action or {}
    action_field = action.get("field", "__action__")
    action_type = action.get("type")
    action_label = action.get("label", "")
    action_color = action.get("color", "info")

    for record in row_data:
        if not isinstance(record, dict):
            continue

        row_id = _stringify_mobile_value(record.get(row_id_field)) if row_id_field else ""
        title_text = _stringify_mobile_value(record.get(title_field)) if title_field else ""
        if not title_text:
            title_text = row_id or "سجل"

        field_nodes = []
        for field in field_order or []:
            if field == title_field or field == row_id_field:
                continue
            value = _stringify_mobile_value(record.get(field))
            if not value:
                continue
            field_nodes.append(
                html.Div(
                    [
                        html.Small(str(field), className="mobile-record-field-label"),
                        html.Div(value, className="mobile-record-field-value"),
                    ],
                    className="mobile-record-field",
                )
            )

        action_nodes = []
        if select_target and row_id:
            action_nodes.append(
                dbc.Button(
                    select_label,
                    id={"type": "mobile-select-row", "target": select_target, "value": row_id},
                    color="primary",
                    outline=True,
                    className="mobile-record-button",
                    n_clicks=0,
                )
            )

        action_value = _stringify_mobile_value(record.get(action_field))
        if action_type and row_id and action_value:
            action_nodes.append(
                dbc.Button(
                    action_label or action_value,
                    id={"type": action_type, "index": row_id},
                    color=action_color,
                    className="mobile-record-button",
                    n_clicks=0,
                )
            )

        records.append(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H5(title_text, className="mobile-record-title"),
                                        html.Small(row_id, className="mobile-record-id") if row_id else None,
                                    ]
                                ),
                            ],
                            className="mobile-record-header",
                        ),
                        html.Div(field_nodes, className="mobile-record-fields") if field_nodes else None,
                        html.Div(action_nodes, className="mobile-record-actions") if action_nodes else None,
                    ]
                ),
                className="mobile-record-card",
            )
        )

    return html.Div(records, className="mobile-record-list")


def build_data_table(
    df,
    table_id="datatable",
    filename=None,
    action_buttons=None,
    row_id_field=None,
    data_cache=None,
    mobile_card_fields=None,
    mobile_title_field=None,
    mobile_select_target=None,
):
    row_data = None

    if data_cache and filename and filename in data_cache and "records" in data_cache[filename]:
        cached_records = data_cache[filename]["records"]
        if len(df) == len(cached_records):
            if len(df) > 1 and df.index[0] > df.index[-1]:
                row_data = cached_records[::-1]
            else:
                row_data = cached_records

    df_view = df.copy()
    column_defs = [{"field": col, "filter": True, "sortable": True} for col in df_view.columns]

    action_field = None
    if action_buttons:
        action_field = action_buttons.get("field", "__action__")
        action_col_id = action_buttons.get("col_id", action_field)
        action_label = action_buttons.get("label", "تفاصيل")
        df_view[action_field] = action_label

        if row_data is not None:
            for rec in row_data:
                rec[action_field] = action_label

        column_defs = [c for c in column_defs if c.get("field") != action_field]
        action_col = {
            "headerName": action_buttons.get("header", ""),
            "field": action_field,
            "colId": action_col_id,
            "minWidth": action_buttons.get("minWidth", 120),
            "maxWidth": action_buttons.get("maxWidth", 150),
            "filter": False,
            "sortable": False,
            "suppressHeaderMenuButton": True,
            "cellClass": "ag-action-cell",
            "cellStyle": {"textAlign": "center"},
        }
        column_defs = [action_col] + column_defs

    if row_data is None:
        row_data = df_view.to_dict("records")

    grid_kwargs = {}
    if row_id_field:
        safe_field = str(row_id_field).replace("\\", "\\\\").replace("'", "\\'")
        grid_kwargs["getRowId"] = f"params.data['{safe_field}']"
        grid_kwargs["dangerously_allow_code"] = True

    data_fields = [
        field for field in df_view.columns
        if field not in {action_field, "__image__"}
    ]
    title_field = mobile_title_field if mobile_title_field in data_fields else _guess_title_field(data_fields)
    field_order = [field for field in (mobile_card_fields or data_fields) if field in data_fields]
    mobile_cards = build_mobile_record_list(
        row_data=row_data,
        row_id_field=row_id_field,
        title_field=title_field,
        field_order=field_order,
        select_target=mobile_select_target,
        action={
            "field": action_field,
            "type": action_buttons.get("mobile_type") if action_buttons else None,
            "label": action_buttons.get("mobile_label", action_buttons.get("label", "")) if action_buttons else "",
            "color": action_buttons.get("mobile_color", "info") if action_buttons else "info",
        },
    )

    export_button = dbc.Button(
        "📥 تنزيل Excel/CSV",
        id={"type": "export-btn", "index": table_id},
        size="sm",
        color="secondary",
        className="mb-2 table-export-btn",
        outline=True,
    )

    grid = dag.AgGrid(
        id={"type": "grid", "index": table_id},
        rowData=row_data,
        columnDefs=column_defs,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "floatingFilter": True,
            "cellStyle": {"textAlign": "center"},
            "headerClass": "text-center-header",
        },
        columnSize="sizeToFit",
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20,
            "paginationPageSizeSelector": [10, 20, 50, 100, 200],
            "csvExportParams": {"fileName": f"{table_id}.csv"},
            "enableRtl": True,
            "enableCellTextSelection": True,
            "ensureDomOrder": True,
        },
        className="ag-theme-alpine",
        style={"height": "70vh", "width": "100%"},
        csvExportParams={"fileName": f"{table_id}.csv"},
        **grid_kwargs,
    )

    return html.Div(
        [
            export_button,
            mobile_cards if mobile_cards is not None else None,
            html.Div(
                grid,
                className="desktop-table-view" if mobile_cards is not None else "desktop-table-view desktop-table-view--force",
            ),
        ]
    )
