from app.table_content.bookings import build_bookings_table_content
from app.table_content.customers import build_customers_table_content
from app.table_content.departments import build_departments_table_content
from app.table_content.dresses import build_dresses_table_content
from app.table_content.payments import build_payments_table_content
from app.table_content.services import build_services_table_content


def make_table_content_builders(
    *,
    load_data,
    create_dt,
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
):
    def get_customers_table_content():
        return build_customers_table_content(
            load_data=load_data,
            create_dt=create_dt,
            c_cols=c_cols,
            customer_bookings_action_label=customer_bookings_action_label,
        )

    def get_services_table_content():
        return build_services_table_content(
            load_data=load_data,
            create_dt=create_dt,
            s_cols=s_cols,
        )

    def get_bookings_table_content():
        return build_bookings_table_content(
            load_data=load_data,
            create_dt=create_dt,
            b_cols=b_cols,
            c_cols=c_cols,
            d_cols=d_cols,
            payments_action_label=payments_action_label,
        )

    def get_payments_table_content():
        return build_payments_table_content(
            load_data=load_data,
            create_dt=create_dt,
            p_cols=p_cols,
            payment_booking_action_label=payment_booking_action_label,
        )

    def get_dresses_table_content():
        return build_dresses_table_content(
            load_data=load_data,
            d_cols=d_cols,
            b_cols=b_cols,
            normalize_code=normalize_code,
            dress_bookings_action_label=dress_bookings_action_label,
        )

    def get_dept_table_content():
        return build_departments_table_content(
            check_departments=check_departments,
            create_dt=create_dt,
        )

    return {
        "customers": get_customers_table_content,
        "services": get_services_table_content,
        "bookings": get_bookings_table_content,
        "payments": get_payments_table_content,
        "dresses": get_dresses_table_content,
        "departments": get_dept_table_content,
    }
