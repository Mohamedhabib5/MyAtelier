from health_check_context import *
from health_check_nav_ids import _collect_component_ids

def _booking_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-booking",
            "b-dept",
            "b-customer",
            "b-service",
            "b-dress",
            "b-date",
            "b-event-date",
            "b-price",
            "b-paid",
            "b-notes",
            "b-alert",
            "btn-save-booking",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _payments_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-payment",
            "p-search",
            "p-date",
            "p-amount",
            "p-booking",
            "p-booking-details",
            "p-notes",
            "p-alert",
            "btn-add-payment-modal",
            "btn-save-payment",
            "btn-edit-payment",
            "btn-delete-payment",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _settings_departments_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "btn-add-dept-modal",
            "dept-search",
            "btn-edit-dept",
            "btn-delete-dept",
            "dept-edit-id",
            "dept-alert",
            "dept-table-container",
            "modal-dept",
            "dept-modal-title",
            "dept-name",
            "btn-save-dept",
            "modal-delete-dept",
            "btn-cancel-delete-dept",
            "btn-confirm-delete-dept",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _delete_confirm_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-delete-customer",
            "btn-cancel-delete",
            "btn-confirm-delete",
            "modal-delete-service",
            "btn-cancel-delete-s",
            "btn-confirm-delete-s",
            "modal-delete-dress",
            "btn-cancel-delete-d",
            "btn-confirm-delete-d",
            "modal-delete-booking",
            "btn-cancel-delete-b",
            "btn-confirm-delete-b",
            "modal-delete-payment",
            "btn-cancel-delete-p",
            "btn-confirm-delete-p",
            "modal-delete-dept",
            "btn-cancel-delete-dept",
            "btn-confirm-delete-dept",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _customers_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-customer",
            "c-name",
            "c-groom",
            "c-phone1",
            "c-phone2",
            "c-addr",
            "c-reg-date",
            "c-notes",
            "c-add-alert",
            "btn-save-customer",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _services_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-service",
            "s-name",
            "s-dept",
            "s-price",
            "s-alert",
            "btn-save-service",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _dresses_form_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "modal-dress",
            "d-code",
            "d-type",
            "d-date",
            "d-status",
            "d-desc",
            "d-upload-image",
            "d-upload-output",
            "d-alert",
            "btn-save-dress",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _quick_add_and_details_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "btn-quick-add-customer",
            "modal-details-viewer",
            "details-viewer-title",
            "details-viewer-body",
            "btn-close-details",
            "p-booking-details",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _auth_error_text_localization_smoke():
    result = {"ok": False, "error": None}
    try:
        path = os.path.join(ROOT, "app", "callbacks", "auth.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        has_ar = "خطأ أثناء تحميل الصفحة" in content
        has_en = "Error Loading Page" in content
        result["ok"] = has_ar and (not has_en)
        if not result["ok"]:
            result["error"] = (
                f"localized_title_present={has_ar}, english_title_present={has_en}"
            )
    except Exception as e:
        result["error"] = str(e)
    return result
