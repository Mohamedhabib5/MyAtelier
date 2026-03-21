import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html

from app.ui.grid import build_mobile_record_list


def build_dresses_table_content(load_data, d_cols, b_cols, normalize_code, dress_bookings_action_label):
    df = load_data("dresses.csv", d_cols)
    if df.empty:
        return html.Div(
            [
                dbc.Alert("لا توجد فساتين.", color="info"),
                dag.AgGrid(
                    id="dresses-table",
                    rowData=[],
                    columnDefs=[],
                    defaultColDef={"resizable": True},
                    style={"display": "none"},
                ),
            ]
        )

    code_col = d_cols[0] if len(d_cols) > 0 else "كود الفستان"
    type_col = d_cols[1] if len(d_cols) > 1 else None
    date_col = d_cols[2] if len(d_cols) > 2 else None
    desc_col = d_cols[3] if len(d_cols) > 3 else None
    image_col = d_cols[4] if len(d_cols) > 4 else None
    status_col = d_cols[5] if len(d_cols) > 5 else None

    booked_codes = set()
    b_df = load_data("bookings.csv", b_cols)
    if not b_df.empty and len(b_cols) > 5 and b_cols[5] in b_df.columns:
        booked_codes = {
            normalize_code(code)
            for code in b_df[b_cols[5]].tolist()
            if normalize_code(code) not in ("", "-", "nan")
        }

    df["__action__"] = df[code_col].apply(
        lambda value: dress_bookings_action_label if normalize_code(value) in booked_codes else ""
    )

    if image_col and image_col in df.columns:
        df["__image__"] = df[image_col].apply(
            lambda name: f"![img](/dress_images/{name})" if str(name).strip() not in ("", "nan", "None") else ""
        )
    else:
        df["__image__"] = ""

    column_defs = [
        {
            "headerName": "",
            "field": "__action__",
            "colId": "view-dress-bookings-action",
            "minWidth": 150,
            "maxWidth": 190,
            "cellClass": "ag-action-cell",
            "filter": False,
            "sortable": False,
        },
        {"headerName": code_col, "field": code_col, "minWidth": 130},
    ]

    if desc_col and desc_col in df.columns:
        column_defs.append({"headerName": desc_col, "field": desc_col, "minWidth": 180, "flex": 1})
    if type_col and type_col in df.columns:
        column_defs.append({"headerName": type_col, "field": type_col, "minWidth": 120})
    if status_col and status_col in df.columns:
        column_defs.append({"headerName": status_col, "field": status_col, "minWidth": 120})
    if date_col and date_col in df.columns:
        column_defs.append({"headerName": date_col, "field": date_col, "minWidth": 130})

    column_defs.append(
        {
            "headerName": "الصورة",
            "field": "__image__",
            "cellRenderer": "markdown",
            "minWidth": 120,
            "maxWidth": 150,
            "filter": False,
            "sortable": False,
        }
    )

    row_data = df.to_dict("records")
    mobile_cards = build_mobile_record_list(
        row_data=row_data,
        row_id_field=code_col,
        title_field=desc_col if desc_col in df.columns else code_col,
        field_order=[type_col, status_col, date_col, code_col],
        select_target="d-search",
        action={
            "field": "__action__",
            "type": "view-dress-bookings",
            "label": dress_bookings_action_label,
            "color": "info",
        },
    )

    grid = dag.AgGrid(
        id="dresses-table",
        rowData=row_data,
        columnDefs=column_defs,
        defaultColDef={"sortable": True, "filter": True, "floatingFilter": True, "resizable": True},
        dashGridOptions={
            "rowHeight": 72,
            "pagination": True,
            "paginationPageSize": 10,
            "paginationPageSizeSelector": [10, 20, 50, 100],
            "enableCellTextSelection": True,
            "ensureDomOrder": True,
        },
        getRowId=f"params.data['{code_col}']",
        dangerously_allow_code=True,
        style={"height": "600px", "width": "100%"},
        className="ag-theme-alpine",
    )

    return html.Div(
        [
            mobile_cards,
            html.Div(grid, className="desktop-table-view"),
        ]
    )
