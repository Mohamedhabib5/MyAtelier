import dash_bootstrap_components as dbc


def build_departments_table_content(check_departments, create_dt):
    df = check_departments()
    if df.empty:
        return dbc.Alert("لا يوجد أقسام", color="info")

    title_field = "department_name" if "department_name" in df.columns else df.columns[0]
    return create_dt(
        df,
        "dept-table",
        "departments.csv",
        row_id_field=title_field,
        mobile_card_fields=[],
        mobile_title_field=title_field,
        mobile_select_target="dept-search",
    )
