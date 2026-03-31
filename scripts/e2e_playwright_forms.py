from e2e_playwright_context import *
from e2e_playwright_dropdowns import _dropdown_selected_text, select_dropdown_or_first, select_dropdown_value
from e2e_playwright_navigation import safe_click, wait_dropdown_ready, wait_for_no_modal, wait_modal_open, wait_visible

def open_quick_customer_modal(page, retries=3):
    for _ in range(retries):
        safe_click(page, "#btn-quick-add-customer")
        try:
            page.evaluate("() => { const el = document.querySelector('#btn-quick-add-customer'); if (el) el.click(); }")
        except Exception:
            pass
        try:
            page.wait_for_selector("#modal-customer .modal-content", state="visible", timeout=4000)
            page.wait_for_selector("#c-name", state="visible", timeout=4000)
            return True
        except PWTimeout:
            page.wait_for_timeout(400)
    return False

def expect_booking_blocked(page, logs_dir, name):
    safe_click(page, "#btn-save-booking")
    # Under heavy backup-on-write load, callback responses can take much longer.
    deadline = time.time() + 120
    while time.time() < deadline:
        blocked_alert = page.locator("#b-alert .alert-danger, #b-alert .alert-warning")
        alert_text = ""
        try:
            if page.locator("#b-alert").count() > 0:
                alert_text = page.locator("#b-alert").inner_text().strip()
        except Exception:
            alert_text = ""
        has_conflict_text = ("محجوز" in alert_text) or ("يوجد حجز" in alert_text)
        if blocked_alert.count() > 0 or has_conflict_text:
            page.screenshot(path=str(logs_dir / f"{name}_blocked.png"))
            try:
                (logs_dir / f"{name}_blocked.txt").write_text(alert_text, encoding="utf-8")
            except Exception:
                pass
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            wait_for_no_modal(page)
            return True
        try:
            modal_visible = page.locator("#modal-booking .modal-content").is_visible()
        except Exception:
            modal_visible = False
        if not modal_visible:
            break
        page.wait_for_timeout(300)
    try:
        alert_text = page.locator("#b-alert").inner_text().strip() if page.locator("#b-alert").count() > 0 else ""
    except Exception:
        alert_text = ""
    page.screenshot(path=str(logs_dir / f"{name}_not_blocked.png"))
    try:
        (logs_dir / f"{name}_not_blocked.txt").write_text(alert_text, encoding="utf-8")
    except Exception:
        pass
    return False

def wait_booking_visible_in_table(page, booking_marker, retries=20, delay_ms=500):
    needle = str(booking_marker).strip()
    if not needle:
        return False
    for _ in range(retries):
        try:
            container = page.locator("#bookings-table-container")
            if container.count() > 0 and container.filter(has_text=needle).count() > 0:
                return True
        except Exception:
            pass
        page.wait_for_timeout(delay_ms)
    return False

def open_booking_modal(page, retries=3):
    for _ in range(retries):
        # Ensure bookings view is visible
        try:
            visible = page.evaluate(
                "() => { const el = document.querySelector('#view-bookings'); return !!(el && el.style.display !== 'none'); }"
            )
            if not visible and page.locator('#nav-bookings').count() > 0:
                safe_click(page, "#nav-bookings")
                page.wait_for_timeout(400)
        except Exception:
            pass
        safe_click(page, "#btn-add-booking-modal")
        try:
            page.evaluate("() => { const el = document.querySelector('#btn-add-booking-modal'); if (el) el.click(); }")
        except Exception:
            pass
        try:
            page.wait_for_selector("#modal-booking .modal-content", state="visible", timeout=4000)
            page.wait_for_selector("#b-dept", state="visible", timeout=4000)
            page.wait_for_timeout(200)
            try:
                if page.locator("#b-dept").is_visible():
                    return True
            except Exception:
                pass
            # If b-dept isn't stable/visible, retry.
        except PWTimeout:
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            wait_for_no_modal(page)
            page.wait_for_timeout(400)
    return False

def ensure_dress_ready(page, timeout=15000, retries=5, dept_text="\u0627\u0644\u0641\u0633\u0627\u062a\u064a\u0646"):
    for _ in range(retries):
        try:
            if page.locator("#b-dress").is_visible():
                return
        except Exception:
            pass
        try:
            select_by_text(page, "b-dept", dept_text)
        except Exception:
            pass
        page.wait_for_timeout(400)
        try:
            if page.locator("#b-dress").is_visible():
                return
        except Exception:
            pass
    try:
        page.wait_for_selector("#dress-section", state="visible", timeout=timeout)
    except Exception:
        pass
    wait_visible(page, "#b-dress", timeout=timeout)

def open_payment_modal(page, retries=3):
    for _ in range(retries):
        try:
            visible = page.evaluate(
                "() => { const el = document.querySelector('#view-payments'); return !!(el && el.style.display !== 'none'); }"
            )
            if not visible and page.locator('#nav-payments').count() > 0:
                safe_click(page, "#nav-payments")
                page.wait_for_timeout(400)
        except Exception:
            pass
        safe_click(page, "#btn-add-payment-modal")
        try:
            page.evaluate("() => { const el = document.querySelector('#btn-add-payment-modal'); if (el) el.click(); }")
        except Exception:
            pass
        try:
            page.wait_for_selector("#modal-payment .modal-content", state="visible", timeout=4000)
            page.wait_for_selector("#p-amount", state="visible", timeout=4000)
            return True
        except PWTimeout:
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            wait_for_no_modal(page)
            page.wait_for_timeout(400)
    return False

def open_customer_modal(page, quick=False, retries=3):
    btn = "#btn-quick-add-customer" if quick else "#btn-add-customer-modal"
    for _ in range(retries):
        safe_click(page, btn)
        try:
            page.evaluate(
                "sel => { const el = document.querySelector(sel); if (el) el.click(); }",
                btn,
            )
        except Exception:
            pass
        try:
            page.wait_for_selector("#modal-customer .modal-content", state="visible", timeout=4000)
            page.wait_for_selector("#c-name", state="visible", timeout=4000)
            return True
        except PWTimeout:
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            wait_for_no_modal(page)
            page.wait_for_timeout(400)
    return False

def open_service_modal(page, retries=3):
    for _ in range(retries):
        try:
            visible = page.evaluate(
                "() => { const el = document.querySelector('#view-services'); return !!(el && el.style.display !== 'none'); }"
            )
            if not visible and page.locator('#nav-services').count() > 0:
                safe_click(page, "#nav-services")
                page.wait_for_timeout(400)
        except Exception:
            pass
        safe_click(page, "#btn-add-service-modal")
        try:
            page.evaluate(
                "sel => { const el = document.querySelector(sel); if (el) el.click(); }",
                "#btn-add-service-modal",
            )
        except Exception:
            pass
        try:
            page.wait_for_selector("#modal-service .modal-content", state="visible", timeout=4000)
            page.wait_for_selector("#s-name", state="visible", timeout=4000)
            return True
        except PWTimeout:
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            wait_for_no_modal(page)
            page.wait_for_timeout(400)
    return False

def open_dress_modal(page, retries=3):
    for _ in range(retries):
        safe_click(page, "#btn-add-dress-modal")
        try:
            page.evaluate(
                "sel => { const el = document.querySelector(sel); if (el) el.click(); }",
                "#btn-add-dress-modal",
            )
        except Exception:
            pass
        try:
            page.wait_for_selector("#modal-dress .modal-content", state="visible", timeout=4000)
            page.wait_for_selector("#d-code", state="visible", timeout=4000)
            return True
        except PWTimeout:
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            wait_for_no_modal(page)
            page.wait_for_timeout(400)
    return False

def ensure_booking_input_visible(page, logs_dir, marker, timeout=3000):
    try:
        page.wait_for_selector("#modal-booking .modal-content", state="visible", timeout=timeout)
        page.wait_for_selector("#b-event-date", state="visible", timeout=timeout)
        return True
    except Exception:
        page.screenshot(path=str(logs_dir / f"{marker}_booking_modal_not_ready.png"))
        return False

def booking_modal_still_open_with_alert(page):
    try:
        open_now = page.locator("#modal-booking .modal-content").is_visible()
    except Exception:
        open_now = False
    alert_text = ""
    if open_now:
        try:
            if page.locator("#b-alert").count() > 0:
                alert_text = page.locator("#b-alert").inner_text().strip()
        except Exception:
            alert_text = ""
    return open_now, alert_text

def click_booking_save(page):
    btn = page.locator("#modal-booking #btn-save-booking")
    btn.wait_for(state="visible", timeout=5000)
    btn.click(force=True)
    try:
        btn.dispatch_event("click")
    except Exception:
        pass
    try:
        page.evaluate(
            "() => { const el = document.querySelector('#modal-booking #btn-save-booking'); if (el) el.click(); }"
        )
    except Exception:
        pass

def dump_booking_save_state(page, logs_dir, marker):
    data = page.evaluate(
        """
        () => {
            const q = (sel) => document.querySelector(sel);
            const txt = (sel) => (q(sel)?.textContent || '').trim();
            const val = (sel) => q(sel)?.value ?? null;
            const attr = (sel, a) => q(sel)?.getAttribute(a);
            const cls = (sel) => q(sel)?.className || '';
            return {
                modal_open: !!q('#modal-booking .modal-content'),
                btn_disabled: !!q('#modal-booking #btn-save-booking')?.disabled,
                btn_loading: attr('#modal-booking #btn-save-booking', 'data-dash-is-loading'),
                dept_text: txt('#b-dept .Select-value-label, #b-dept .Select-value'),
                customer_text: txt('#b-customer .Select-value-label, #b-customer .Select-value'),
                service_text: txt('#b-service .Select-value-label, #b-service .Select-value'),
                dress_text: txt('#b-dress .Select-value-label, #b-dress .Select-value'),
                event_date: val('#b-event-date'),
                price: val('#b-price'),
                paid: val('#b-paid'),
                alert_text: txt('#b-alert'),
                alert_class: cls('#b-alert .alert'),
            };
        }
        """
    )
    out = logs_dir / f"{marker}_booking_save_state.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_booking_required_selected(page, logs_dir, marker):
    required_ids = ("b-dept", "b-customer", "b-service", "b-dress")
    missing = []
    for did in required_ids:
        txt = _dropdown_selected_text(page, did)
        if not txt or txt.startswith("اختر"):
            missing.append(did)
    if missing:
        page.screenshot(path=str(logs_dir / f"{marker}_required_dropdowns_missing.png"))
        with open(logs_dir / f"{marker}_required_dropdowns_missing.txt", "w", encoding="utf-8") as f:
            f.write(",".join(missing))
        return False
    return True

def create_test_images(logs_dir):
    big_path = logs_dir / "e2e_big.png"
    small_path = logs_dir / "e2e_small.png"

    # Big image (>300KB) - random noise to reduce compression
    w, h = 800, 800
    img = Image.frombytes("RGB", (w, h), os.urandom(w * h * 3))
    img.save(big_path, format="PNG", compress_level=0)

    # Small image (<300KB)
    w2, h2 = 200, 200
    img2 = Image.new("RGB", (w2, h2), (120, 150, 200))
    img2.save(small_path, format="PNG", compress_level=9)

    return big_path, small_path
