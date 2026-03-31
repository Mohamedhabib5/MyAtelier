def build_catalog_exports(context):
    c = context

    def check_departments():
        return c["logic_departments_api_domain"].check_departments(
            c["_with_synced_sessionlocal"],
            c["settings_dept_domain"],
            [c["DEPT_MAKEUP"], c["DEPT_PHOTO"], c["DEPT_DRESSES"], c["DEPT_HAIR"], c["DEPT_SKIN"]],
        )

    def add_department(name):
        return c["logic_departments_api_domain"].add_department(
            c["departments_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["settings_dept_domain"],
            c["_invalidate_after_write"],
            c["_invalidate_many"],
            name=name,
            msg_missing_info=c["MSG_MISSING_INFO"],
            msg_already_exists=c["MSG_ALREADY_EXISTS"],
            msg_added=c["MSG_ADDED"],
        )

    def update_department(old_name, new_name):
        return c["logic_departments_api_domain"].update_department(
            c["departments_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["settings_dept_domain"],
            c["_invalidate_after_write"],
            c["_invalidate_many"],
            old_name=old_name,
            new_name=new_name,
            msg_not_found=c["MSG_NOT_FOUND"],
            msg_already_exists=c["MSG_ALREADY_EXISTS"],
            msg_updated=c["MSG_UPDATED"],
        )

    def delete_department(name):
        return c["logic_departments_api_domain"].delete_department(
            c["departments_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["settings_dept_domain"],
            c["_invalidate_after_write"],
            c["_invalidate_many"],
            name=name,
            msg_not_found=c["MSG_NOT_FOUND"],
            msg_in_use=c["MSG_IN_USE"],
            msg_deleted=c["MSG_DELETED"],
        )

    def save_department(name):
        return c["logic_departments_api_domain"].save_department(c["departments_facade_domain"], add_department, name)

    def add_customer(name, groom, phone1, phone2, address, reg_date=None, notes=""):
        return c["logic_customers_api_domain"].add_customer(
            c["customers_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["customers_domain"],
            c["_invalidate_after_write"],
            name=name,
            groom=groom,
            phone1=phone1,
            phone2=phone2,
            address=address,
            reg_date=reg_date,
            notes=notes,
            msg_missing_info=c["MSG_MISSING_INFO"],
            msg_invalid_phone=c["MSG_INVALID_PHONE"],
            msg_added=c["MSG_ADDED"],
        )

    def update_customer(c_id, name, groom, phone1, phone2, address, reg_date=None, notes=""):
        return c["logic_customers_api_domain"].update_customer(
            c["customers_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["customers_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            c_id=c_id,
            name=name,
            groom=groom,
            phone1=phone1,
            phone2=phone2,
            address=address,
            reg_date=reg_date,
            notes=notes,
            msg_missing_info=c["MSG_MISSING_INFO"],
            msg_not_found=c["MSG_NOT_FOUND"],
            msg_phone_used_by_another=c["MSG_PHONE_USED_BY_ANOTHER"],
            msg_updated=c["MSG_UPDATED"],
        )

    def delete_customer(c_id):
        return c["logic_customers_api_domain"].delete_customer(
            c["customers_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["customers_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            c_id=c_id,
            msg_not_found=c["MSG_NOT_FOUND"],
            msg_has_bookings=c["MSG_HAS_BOOKINGS"],
            msg_deleted=c["MSG_DELETED"],
        )

    def add_service(name, dept, price):
        return c["logic_services_api_domain"].add_service(
            c["services_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["services_domain"],
            c["_invalidate_after_write"],
            name=name,
            dept=dept,
            price=price,
            money_float_fn=c["_money_float"],
            msg_missing_info=c["MSG_MISSING_INFO"],
            msg_added=c["MSG_ADDED"],
        )

    def update_service(s_id, name, dept, price):
        return c["logic_services_api_domain"].update_service(
            c["services_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["services_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            s_id=s_id,
            name=name,
            dept=dept,
            price=price,
            money_float_fn=c["_money_float"],
            msg_updated=c["MSG_UPDATED"],
            msg_not_found=c["MSG_NOT_FOUND"],
        )

    def delete_service(s_id):
        return c["logic_services_api_domain"].delete_service(
            c["services_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["services_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            s_id=s_id,
            msg_not_found=c["MSG_NOT_FOUND"],
            msg_has_bookings=c["MSG_HAS_BOOKINGS"],
            msg_deleted=c["MSG_DELETED"],
        )

    def save_image(image_contents, dress_code):
        return c["logic_dresses_api_domain"].save_image(
            c["dresses_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["dresses_domain"],
            image_contents=image_contents,
            dress_code=dress_code,
            image_folder=c["IMAGE_FOLDER"],
        )

    def add_dress(code, d_type, date_buy, status, desc, image_contents=None):
        return c["logic_dresses_api_domain"].add_dress(
            c["dresses_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["dresses_domain"],
            c["_invalidate_after_write"],
            code=code,
            d_type=d_type,
            date_buy=date_buy,
            status=status,
            desc=desc,
            image_contents=image_contents,
            image_folder=c["IMAGE_FOLDER"],
            msg_missing_info=c["MSG_MISSING_INFO"],
            msg_code_exists=c["MSG_CODE_EXISTS"],
            msg_added=c["MSG_ADDED"],
        )

    def update_dress(old_code, new_code, d_type, date_buy, status, desc, image_contents=None):
        return c["logic_dresses_api_domain"].update_dress(
            c["dresses_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["dresses_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            old_code=old_code,
            new_code=new_code,
            d_type=d_type,
            date_buy=date_buy,
            status=status,
            desc=desc,
            image_contents=image_contents,
            image_folder=c["IMAGE_FOLDER"],
            msg_not_found=c["MSG_NOT_FOUND"],
            msg_new_code_exists=c["MSG_NEW_CODE_EXISTS"],
            msg_updated=c["MSG_UPDATED"],
        )

    def delete_dress(d_code):
        return c["logic_dresses_api_domain"].delete_dress(
            c["dresses_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["dresses_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            d_code=d_code,
            image_folder=c["IMAGE_FOLDER"],
            msg_not_found=c["MSG_NOT_FOUND"],
            msg_has_bookings=c["MSG_HAS_BOOKINGS"],
            msg_deleted=c["MSG_DELETED"],
        )

    return {
        "check_departments": check_departments,
        "add_department": add_department,
        "update_department": update_department,
        "delete_department": delete_department,
        "save_department": save_department,
        "add_customer": add_customer,
        "update_customer": update_customer,
        "delete_customer": delete_customer,
        "add_service": add_service,
        "update_service": update_service,
        "delete_service": delete_service,
        "save_image": save_image,
        "add_dress": add_dress,
        "update_dress": update_dress,
        "delete_dress": delete_dress,
    }
