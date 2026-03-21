from app.composition.layout_factory import make_main_layout
from app.table_content.factory import make_table_content_builders
from app.ui.grid import build_data_table


def build_runtime_wiring(
    *,
    load_data,
    data_cache,
    check_departments,
    c_cols,
    s_cols,
    d_cols,
    b_cols,
    p_cols,
    normalize_code,
    payments_action_label,
    customer_bookings_action_label,
    dress_bookings_action_label,
    payment_booking_action_label,
    layout_finance,
    layout_bookings,
    layout_customers,
    layout_services,
    layout_dresses,
    layout_payments,
    layout_settings,
    backup_folder,
    layout_users,
):
    def create_dt(
        df,
        table_id="datatable",
        filename=None,
        action_buttons=None,
        row_id_field=None,
        mobile_card_fields=None,
        mobile_title_field=None,
        mobile_select_target=None,
    ):
        return build_data_table(
            df=df,
            table_id=table_id,
            filename=filename,
            action_buttons=action_buttons,
            row_id_field=row_id_field,
            data_cache=data_cache,
            mobile_card_fields=mobile_card_fields,
            mobile_title_field=mobile_title_field,
            mobile_select_target=mobile_select_target,
        )

    table_content_builders = make_table_content_builders(
        load_data=load_data,
        create_dt=create_dt,
        check_departments=check_departments,
        c_cols=c_cols,
        s_cols=s_cols,
        d_cols=d_cols,
        b_cols=b_cols,
        p_cols=p_cols,
        normalize_code=normalize_code,
        payments_action_label=payments_action_label,
        customer_bookings_action_label=customer_bookings_action_label,
        dress_bookings_action_label=dress_bookings_action_label,
        payment_booking_action_label=payment_booking_action_label,
    )

    main_layout = make_main_layout(
        layout_finance=layout_finance,
        layout_bookings=layout_bookings,
        check_departments=check_departments,
        get_bookings_table_content=table_content_builders["bookings"],
        layout_customers=layout_customers,
        get_customers_table_content=table_content_builders["customers"],
        load_data=load_data,
        c_cols=c_cols,
        layout_services=layout_services,
        get_services_table_content=table_content_builders["services"],
        layout_dresses=layout_dresses,
        get_dresses_table_content=table_content_builders["dresses"],
        layout_payments=layout_payments,
        get_payments_table_content=table_content_builders["payments"],
        layout_settings=layout_settings,
        backup_folder=backup_folder,
        get_dept_table_content=table_content_builders["departments"],
        layout_users=layout_users,
    )

    return {
        "create_dt": create_dt,
        "main_layout": main_layout,
        "get_customers_table_content": table_content_builders["customers"],
        "get_services_table_content": table_content_builders["services"],
        "get_bookings_table_content": table_content_builders["bookings"],
        "get_payments_table_content": table_content_builders["payments"],
        "get_dresses_table_content": table_content_builders["dresses"],
        "get_dept_table_content": table_content_builders["departments"],
    }
