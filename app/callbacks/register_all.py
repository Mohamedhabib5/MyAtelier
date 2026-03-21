from app.callbacks.auth import register_auth_callbacks
from app.callbacks.details_actions import register_details_actions_callback
from app.callbacks.export import register_export_callbacks
from app.callbacks.finance import register_finance_callbacks
from app.callbacks.mobile_cards import register_mobile_card_callbacks
from app.callbacks.navigation import register_navigation_callbacks
from app.callbacks.bookings_form import register_bookings_form_callbacks
from app.callbacks.bookings_search import register_bookings_search_callbacks
from app.callbacks.customers_form import register_customers_form_callbacks
from app.callbacks.customers_search import register_customers_search_callbacks
from app.callbacks.dresses_form import register_dresses_form_callbacks
from app.callbacks.dresses_search import register_dresses_search_callbacks
from app.callbacks.payments_form import register_payments_form_callbacks
from app.callbacks.payments_search import register_payments_search_callbacks
from app.callbacks.services_form import register_services_form_callbacks
from app.callbacks.services_search import register_services_search_callbacks
from app.callbacks.settings_backup import register_settings_backup_callbacks
from app.callbacks.settings_departments import register_settings_departments_callbacks
from app.callbacks.users import register_users_callbacks


def register_all_callbacks(
    app,
    load_data,
    login_layout,
    main_layout,
    verify_password,
    check_departments,
    check_users,
    create_dt,
    logic_module,
    c_cols,
    s_cols,
    d_cols,
    b_cols,
    p_cols,
    normalize_code,
    delete_reason,
    payments_action_label,
    customer_bookings_action_label,
    dress_bookings_action_label,
    payment_booking_action_label,
    get_services_table_content,
    get_dresses_table_content,
    get_payments_table_content,
    get_dept_table_content,
    get_customers_table_content,
    get_bookings_table_content,
):
    register_auth_callbacks(
        app=app,
        login_layout=login_layout,
        main_layout=main_layout,
        check_users=check_users,
        verify_password=verify_password,
    )
    register_navigation_callbacks(app=app)
    register_finance_callbacks(app=app, load_data=load_data, p_cols=p_cols, b_cols=b_cols)
    register_mobile_card_callbacks(app=app)
    register_export_callbacks(app=app)

    register_services_search_callbacks(app, load_data, s_cols)
    register_services_form_callbacks(
        app,
        load_data,
        s_cols,
        get_services_table_content,
        logic_module,
        delete_reason,
    )

    register_dresses_search_callbacks(app, load_data, d_cols)
    register_dresses_form_callbacks(
        app,
        load_data,
        d_cols,
        get_dresses_table_content,
        logic_module,
        delete_reason,
    )

    register_payments_search_callbacks(app, load_data, p_cols)
    register_payments_form_callbacks(
        app,
        load_data,
        b_cols,
        p_cols,
        get_payments_table_content,
        logic_module,
    )

    register_settings_backup_callbacks(app)
    register_settings_departments_callbacks(
        app,
        check_departments,
        load_data,
        s_cols,
        b_cols,
        get_dept_table_content,
    )

    register_users_callbacks(app, check_users, create_dt)

    register_customers_search_callbacks(app, load_data, c_cols)
    register_customers_form_callbacks(
        app,
        load_data,
        c_cols,
        get_customers_table_content,
        logic_module,
        delete_reason,
    )

    register_bookings_search_callbacks(app, load_data, b_cols)
    register_bookings_form_callbacks(
        app,
        load_data,
        c_cols,
        s_cols,
        d_cols,
        b_cols,
        logic_module._is_dresses_dept,
        normalize_code,
        get_bookings_table_content,
        get_dresses_table_content,
        get_payments_table_content,
        logic_module,
        delete_reason,
    )

    register_details_actions_callback(
        app=app,
        load_data=load_data,
        c_cols=c_cols,
        b_cols=b_cols,
        p_cols=p_cols,
        normalize_code=normalize_code,
        payments_action_label=payments_action_label,
        customer_bookings_action_label=customer_bookings_action_label,
        dress_bookings_action_label=dress_bookings_action_label,
        payment_booking_action_label=payment_booking_action_label,
    )
