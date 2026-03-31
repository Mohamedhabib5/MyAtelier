"""Helpers for details-view callback action-cell detection."""


def parse_grid_cell_clicked(cell_clicked):
    """Return normalized fields from an AG Grid cell-click payload."""
    if not isinstance(cell_clicked, dict):
        return {
            "col_id": None,
            "field": None,
            "value": None,
            "row_id": None,
            "value_formatted": None,
            "displayed_value": None,
            "cell_class": None,
            "data_action": None,
            "data": {},
        }

    col_def = cell_clicked.get("colDef") or {}
    data = cell_clicked.get("data") or {}
    return {
        "col_id": cell_clicked.get("colId") or cell_clicked.get("columnId"),
        "field": cell_clicked.get("field") or col_def.get("field"),
        "value": cell_clicked.get("value"),
        "row_id": cell_clicked.get("rowId"),
        "value_formatted": cell_clicked.get("valueFormatted"),
        "displayed_value": cell_clicked.get("displayedValue"),
        "cell_class": col_def.get("cellClass"),
        "data_action": data.get("__action__"),
        "data": data,
    }


def _normalize_action_text(value):
    return str(value).strip() if value is not None else ""


def _is_action_cell_class(cell_class):
    return cell_class == "ag-action-cell" or (
        isinstance(cell_class, (list, tuple)) and "ag-action-cell" in cell_class
    )


def is_grid_action_click(
    parsed_cell,
    action_label,
    action_col_ids=(),
    *,
    include_action_field=True,
    include_action_cell_class=False,
    include_data_action=False,
    strip_values=False,
):
    """Check whether parsed AG Grid click payload represents an action-cell click."""
    col_id = parsed_cell.get("col_id")
    field = parsed_cell.get("field")
    value = parsed_cell.get("value")
    value_formatted = parsed_cell.get("value_formatted")
    displayed_value = parsed_cell.get("displayed_value")

    if col_id in action_col_ids:
        return True
    if include_action_field and field == "__action__":
        return True

    if strip_values:
        label = _normalize_action_text(action_label)
        value_matches = (
            _normalize_action_text(value) == label
            or _normalize_action_text(value_formatted) == label
            or _normalize_action_text(displayed_value) == label
        )
    else:
        value_matches = (
            value == action_label
            or value_formatted == action_label
            or displayed_value == action_label
        )
    if value_matches:
        return True

    if include_data_action:
        data_action = parsed_cell.get("data_action")
        if strip_values:
            if _normalize_action_text(data_action) == _normalize_action_text(action_label):
                return True
        elif data_action == action_label:
            return True

    if include_action_cell_class and _is_action_cell_class(parsed_cell.get("cell_class")):
        return True

    return False
