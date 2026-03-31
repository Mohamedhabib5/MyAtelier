def build_booking_exports(context, add_payment):
    c = context

    def add_booking(customer_name, dept, service, dress_code, event_date, price, paid, status=None, notes="", reg_date=None):
        return c["logic_bookings_api_domain"].add_booking(
            c["bookings_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["bookings_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            customer_name=customer_name,
            dept=dept,
            service=service,
            dress_code=dress_code,
            event_date=event_date,
            price=price,
            paid=paid,
            status=status or c["BOOKING_STATUS_ACTIVE"],
            notes=notes,
            reg_date=reg_date,
            canonical_department_fn=c["resolvers_domain"].canonical_department_name,
            find_customer_fn=c["resolvers_domain"].find_customer_by_name_or_id,
            find_service_fn=c["resolvers_domain"].find_service_by_name_or_id,
            is_no_dress_fn=c["_is_no_dress"],
            money_fn=c["_money"],
            money_float_fn=c["_money_float"],
            add_payment_fn=add_payment,
            dept_map=c["BOOKING_DEPT_MAP"],
            booking_status_active=c["BOOKING_STATUS_ACTIVE"],
            note_booking_downpay=c["NOTE_BOOKING_DOWNPAY"],
            msg_dress_booked_same_date=c["MSG_DRESS_BOOKED_SAME_DATE"],
            msg_invalid_value=c["MSG_INVALID_VALUE"],
            msg_paid_gt_price=c["MSG_PAID_GT_PRICE"],
        )

    def update_booking(b_id, customer_name, dept, service, dress_code, event_date, price, paid, status, notes):
        return c["logic_bookings_api_domain"].update_booking(
            c["bookings_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["bookings_domain"],
            c["_invalidate_after_write"],
            b_id=b_id,
            customer_name=customer_name,
            dept=dept,
            service=service,
            dress_code=dress_code,
            event_date=event_date,
            price=price,
            paid=paid,
            status=status,
            notes=notes,
            canonical_department_fn=c["resolvers_domain"].canonical_department_name,
            find_customer_fn=c["resolvers_domain"].find_customer_by_name_or_id,
            find_service_fn=c["resolvers_domain"].find_service_by_name_or_id,
            is_no_dress_fn=c["_is_no_dress"],
            money_fn=c["_money"],
            money_float_fn=c["_money_float"],
            booking_status_active=c["BOOKING_STATUS_ACTIVE"],
            msg_dress_booked_same_date=c["MSG_DRESS_BOOKED_SAME_DATE"],
            msg_invalid_value=c["MSG_INVALID_VALUE"],
            msg_paid_gt_price=c["MSG_PAID_GT_PRICE"],
        )

    def delete_booking(b_id):
        return c["logic_bookings_api_domain"].delete_booking(
            c["bookings_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["bookings_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            b_id=b_id,
        )

    return {
        "add_booking": add_booking,
        "update_booking": update_booking,
        "delete_booking": delete_booking,
    }
