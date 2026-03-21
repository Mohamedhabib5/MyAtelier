def build_services_table_content(load_data, create_dt, s_cols):
    df = load_data("services.csv", s_cols)
    return create_dt(
        df,
        "services-table",
        "services.csv",
        row_id_field=s_cols[0] if s_cols else None,
        mobile_card_fields=[s_cols[1], s_cols[3]] if len(s_cols) > 3 else s_cols[1:3],
        mobile_title_field=s_cols[2] if len(s_cols) > 2 else (s_cols[0] if s_cols else None),
        mobile_select_target="s-search",
    )
