from e2e_playwright_context import *
from e2e_playwright_helpers import *

def run_booking_only(page, logs_dir, ts, today, tomorrow, same_day, bride_booking, bride_booking2, service_used, dress_used, dress_unused):
    errors = []
    page.set_default_timeout(25000)

    print("[BOOKING_ONLY] step 1: create service")
    open_tab(page, "#nav-services", "#view-services", "#btn-add-service-modal")
    safe_click(page, "#btn-add-service-modal")
    page.wait_for_selector("#s-name", state="visible")
    page.fill("#s-name", service_used)
    try:
        select_first_option(page, "s-dept")
    except Exception:
        errors.append("Failed to select service department.")
    page.fill("#s-price", "500")
    safe_click(page, "#btn-save-service")
    wait_for_no_modal(page)
    page.wait_for_timeout(500)

    print("[BOOKING_ONLY] step 2: create customer")
    phone_booking = "01" + str(ts)[-9:]
    open_tab(page, "#nav-customers", "#view-customers", "#btn-add-customer-modal")
    if not open_customer_modal(page):
        errors.append("Customer modal did not open.")
    else:
        page.fill("#c-name", bride_booking)
        page.fill("#c-groom", f"{bride_booking} Groom")
        page.fill("#c-phone1", phone_booking)
        page.fill("#c-phone2", phone_booking)
        page.fill("#c-addr", "E2E Address")
        page.fill("#c-notes", "E2E booking smoke")
        safe_click(page, "#btn-save-customer")
        wait_for_no_modal(page)
        page.wait_for_timeout(400)

    print("[BOOKING_ONLY] step 3: create booking")
    open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
    if not open_booking_modal(page):
        errors.append("Booking modal did not open.")
    else:
        try:
            select_first_option(page, "b-dept")
        except Exception:
            errors.append("Failed to select booking department.")
        if not select_dropdown_or_first(page, "b-customer", bride_booking):
            errors.append("Failed to select booking customer.")
        if not select_dropdown_or_first(page, "b-service", service_used):
            errors.append("Failed to select booking service.")
        try:
            dress_visible = page.evaluate(
                "() => { const el = document.querySelector('#dress-section'); return !!(el && el.style.display !== 'none'); }"
            )
        except Exception:
            dress_visible = False
        if dress_visible:
            ensure_dress_ready(page)
            if not select_dropdown_or_first(page, "b-dress", dress_used):
                errors.append("Failed to select booking dress.")
        page.fill("#b-event-date", same_day)
        page.fill("#b-price", "1000")
        page.fill("#b-paid", "200")
        try:
            page.locator("#b-modal-title").click(force=True)
            page.wait_for_timeout(200)
        except Exception:
            pass
        click_booking_save(page)
        wait_for_no_modal(page)
        page.wait_for_timeout(500)

    page.screenshot(path=str(logs_dir / "e2e_booking_smoke_done.png"))

    if errors:
        for e in errors:
            print("Error:", e)
        raise SystemExit(1)

def run_core_smoke(page, logs_dir, ts, service_used, bride_booking):
    errors = []
    page.set_default_timeout(25000)

    print("[CORE_SMOKE] step 1: services")
    open_tab(page, "#nav-services", "#view-services", "#btn-add-service-modal")
    safe_click(page, "#btn-add-service-modal")
    page.wait_for_selector("#s-name", state="visible")
    page.fill("#s-name", service_used)
    try:
        select_first_option(page, "s-dept")
    except Exception:
        errors.append("Failed to select service department in core smoke.")
    page.fill("#s-price", "450")
    safe_click(page, "#btn-save-service")
    wait_for_no_modal(page)
    if not wait_success_toast(page, timeout_ms=9000):
        errors.append("Success toast did not appear after service save in core smoke.")
        page.screenshot(path=str(logs_dir / "e2e_core_smoke_toast_missing_after_service_save.png"))
    page.wait_for_timeout(400)

    print("[CORE_SMOKE] step 2: customers")
    phone_booking = "01" + str(ts)[-9:]
    open_tab(page, "#nav-customers", "#view-customers", "#btn-add-customer-modal")
    if not open_customer_modal(page):
        errors.append("Customer modal did not open in core smoke.")
    else:
        page.fill("#c-name", bride_booking)
        page.fill("#c-groom", f"{bride_booking} Groom")
        page.fill("#c-phone1", phone_booking)
        page.fill("#c-phone2", phone_booking)
        page.fill("#c-addr", "E2E Core Smoke Address")
        page.fill("#c-notes", "E2E core smoke")
        safe_click(page, "#btn-save-customer")
        wait_for_no_modal(page)
        page.wait_for_timeout(400)

    print("[CORE_SMOKE] step 3: payments view")
    open_tab(page, "#nav-payments", "#view-payments", "#btn-add-payment-modal")
    if not open_payment_modal(page):
        errors.append("Payment modal did not open in core smoke.")
    elif page.locator("#p-booking").count() == 0:
        errors.append("Payment modal did not render booking selector.")
    else:
        # Validate required-field warning path: save with missing booking/amount.
        safe_click(page, "#btn-save-payment")
        payment_warning = wait_warning_alert(page, "#p-alert .alert-warning", timeout_ms=7000)
        if (not payment_warning) and (not is_disabled(page, "#btn-save-payment")):
            errors.append("Payment required-fields warning was not shown in core smoke.")
            page.screenshot(path=str(logs_dir / "e2e_core_smoke_payment_required_warning_missing.png"))
        safe_click(page, "#modal-payment .btn-close")
        wait_for_no_modal(page)
    page.screenshot(path=str(logs_dir / "e2e_core_smoke_done.png"))

    if errors:
        for e in errors:
            print("Error:", e)
        raise SystemExit(1)

def run_full_phase1b1(page, logs_dir, ts, service_used, service_unused, bride_delete, bride_booking, bride_booking2):
    errors = []
    page.set_default_timeout(25000)
    print("[FULL_PHASE1B1] step 1: services add")

    open_tab(page, "#nav-services", "#view-services", "#btn-add-service-modal")
    if not export_current_table(page, logs_dir, "services", "#view-services"):
        errors.append("Services export failed.")

    if not open_service_modal(page):
        errors.append("Service modal did not open.")
    else:
        page.fill("#s-name", service_used)
        try:
            select_first_option(page, "s-dept")
        except Exception:
            errors.append("Failed to select service department (used).")
        page.fill("#s-price", "500")
        safe_click(page, "#btn-save-service")
        wait_for_no_modal(page)
        page.wait_for_timeout(400)

    if not open_service_modal(page):
        errors.append("Service modal did not open (unused).")
    else:
        page.fill("#s-name", service_unused)
        try:
            select_first_option(page, "s-dept")
        except Exception:
            errors.append("Failed to select service department (unused).")
        page.fill("#s-price", "450")
        safe_click(page, "#btn-save-service")
        wait_for_no_modal(page)
        page.wait_for_timeout(400)

    print("[FULL_PHASE1B1] step 2: customers add")
    phone_delete = "01" + str(ts)[-9:]
    phone_booking = "01" + str(ts + 1)[-9:]
    phone_booking2 = "01" + str(ts + 2)[-9:]

    open_tab(page, "#nav-customers", "#view-customers", "#btn-add-customer-modal")
    if not export_current_table(page, logs_dir, "customers", "#view-customers"):
        errors.append("Customers export failed.")

    def _add_customer(name, phone, notes):
        if not open_customer_modal(page):
            errors.append(f"Customer modal did not open ({name}).")
            return
        page.fill("#c-name", name)
        page.fill("#c-groom", f"{name} Groom")
        page.fill("#c-phone1", phone)
        page.fill("#c-phone2", phone)
        page.fill("#c-addr", "E2E Address")
        page.fill("#c-notes", notes)
        safe_click(page, "#btn-save-customer")
        wait_for_no_modal(page)
        page.wait_for_timeout(300)

    _add_customer(bride_delete, phone_delete, "E2E customer delete")
    _add_customer(bride_booking, phone_booking, "E2E customer booking")
    _add_customer(bride_booking2, phone_booking2, "E2E customer booking delete")

    page.screenshot(path=str(logs_dir / "e2e_full_phase1b1_done.png"))
    if errors:
        for e in errors:
            print("Error:", e)
        raise SystemExit(1)
