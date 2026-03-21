from app.layouts.main import layout_main


def make_main_layout(
    *,
    layout_finance,
    layout_bookings,
    check_departments,
    get_bookings_table_content,
    layout_customers,
    get_customers_table_content,
    load_data,
    c_cols,
    layout_services,
    get_services_table_content,
    layout_dresses,
    get_dresses_table_content,
    layout_payments,
    get_payments_table_content,
    layout_settings,
    backup_folder,
    get_dept_table_content,
    layout_users,
):
    def _main_layout(user_data):
        return layout_main(
            user_data=user_data,
            layout_finance=layout_finance,
            layout_bookings=layout_bookings,
            check_departments=check_departments,
            get_bookings_table_content=get_bookings_table_content,
            layout_customers=layout_customers,
            get_customers_table_content=get_customers_table_content,
            load_data=load_data,
            c_cols=c_cols,
            layout_services=layout_services,
            get_services_table_content=get_services_table_content,
            layout_dresses=layout_dresses,
            get_dresses_table_content=get_dresses_table_content,
            layout_payments=layout_payments,
            get_payments_table_content=get_payments_table_content,
            layout_settings=layout_settings,
            backup_folder=backup_folder,
            get_dept_table_content=get_dept_table_content,
            layout_users=layout_users,
        )

    return _main_layout
