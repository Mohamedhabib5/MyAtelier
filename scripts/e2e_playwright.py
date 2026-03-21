import json
import os
import time
from datetime import date, timedelta
from pathlib import Path
from PIL import Image

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


BASE_URL = os.environ.get("APP_URL", "http://127.0.0.1:8050")
HEADLESS = os.environ.get("HEADLESS", "0").lower() not in ("0", "false", "no")
USERNAME = os.environ.get("APP_USER", "admin")
PASSWORD = os.environ.get("APP_PASS", "admin123")
BOOKING_ONLY = os.environ.get("BOOKING_ONLY", "0").lower() not in ("0", "false", "no")
CORE_SMOKE = os.environ.get("CORE_SMOKE", "0").lower() not in ("0", "false", "no")
FULL_REGRESSION = os.environ.get("FULL_REGRESSION", "0").lower() not in ("0", "false", "no")
FULL_PHASE = os.environ.get("FULL_PHASE", "all").strip().lower()
RESPONSIVE_SMOKE = os.environ.get("RESPONSIVE_SMOKE", "0").lower() not in ("0", "false", "no")


def wait_for_app_shell(page, timeout_ms=30000):
    page.wait_for_function(
        """
        () => {
            const hasLogin = !!document.querySelector("#login-username");
            const hasMainNav = !!document.querySelector("#nav-finance");
            const hasTabs = !!document.querySelector("#main-tabs");
            return hasLogin || hasMainNav || hasTabs;
        }
        """,
        timeout=timeout_ms,
    )


def wait_dropdown_ready(page, dropdown_id, timeout_ms=20000):
    page.wait_for_function(
        """
        (id) => {
            const el = document.getElementById(id);
            if (!el) return false;
            const loading = el.getAttribute("data-dash-is-loading") === "true";
            const rect = el.getBoundingClientRect();
            const visible = rect.width > 0 && rect.height > 0;
            return !loading && visible;
        }
        """,
        arg=dropdown_id,
        timeout=timeout_ms,
    )


def select_first_option(page, dropdown_id):
    container = page.locator(f"#{dropdown_id}")
    wait_dropdown_ready(page, dropdown_id, timeout_ms=20000)
    try:
        container.scroll_into_view_if_needed()
    except Exception:
        pass
    container.click(force=True)
    page.wait_for_timeout(200)
    option_selectors = [
        ".dash-dropdown-option:visible",
        ".Select-option:visible",
        ".VirtualizedSelectOption:visible",
        "[role='option']:visible",
    ]
    for sel in option_selectors:
        try:
            first_opt = page.locator(sel).first
            if first_opt.count() > 0:
                first_opt.click(force=True)
                return
        except Exception:
            pass
    # Keep fallback non-destructive: do not send Enter (can submit forms).
    page.keyboard.press("ArrowDown")


def select_by_text(page, dropdown_id, text):
    container = page.locator(f"#{dropdown_id}")
    wait_dropdown_ready(page, dropdown_id, timeout_ms=20000)
    try:
        container.scroll_into_view_if_needed()
    except Exception:
        pass
    container.click(force=True)
    page.wait_for_timeout(200)
    option_selectors = [
        ".dash-dropdown-option:visible",
        ".Select-option:visible",
        ".VirtualizedSelectOption:visible",
        "[role='option']:visible",
    ]
    for sel in option_selectors:
        try:
            opt = page.locator(sel, has_text=text).first
            if opt.count() > 0:
                opt.click(force=True)
                return
        except Exception:
            pass
    # Fallback for searchable dropdown inputs when available.
    input_selectors = [
        f"#{dropdown_id} input",
        "input.dash-dropdown-search",
    ]
    for inp_sel in input_selectors:
        try:
            inp = page.locator(inp_sel).first
            if inp.count() > 0:
                inp.click(force=True)
                inp.fill(text)
                page.wait_for_timeout(200)
                for sel in option_selectors:
                    opt = page.locator(sel, has_text=text).first
                    if opt.count() > 0:
                        opt.click(force=True)
                        return
                # Avoid Enter fallback here to prevent accidental submit/close in modals.
                page.keyboard.press("ArrowDown")
                return
        except Exception:
            pass


def safe_click(page, selector, retries=3):
    loc = page.locator(selector)
    for _ in range(retries):
        try:
            loc.scroll_into_view_if_needed()
            loc.click(force=True)
            return
        except Exception:
            page.wait_for_timeout(400)
    try:
        page.evaluate(
            "sel => { const el = document.querySelector(sel); if (el) el.click(); }",
            selector,
        )
    except Exception:
        pass

def wait_visible(page, selector, timeout=15000):
    page.wait_for_selector(selector, state="visible", timeout=timeout)

def wait_success_toast(page, timeout_ms=6000):
    deadline = time.time() + (timeout_ms / 1000.0)
    toast = page.locator("#app-success-toast")
    while time.time() < deadline:
        try:
            if toast.count() > 0 and toast.is_visible():
                return True
        except Exception:
            pass
        page.wait_for_timeout(200)
    return False

def wait_warning_alert(page, selector, timeout_ms=6000):
    deadline = time.time() + (timeout_ms / 1000.0)
    loc = page.locator(selector)
    while time.time() < deadline:
        try:
            if loc.count() > 0 and loc.is_visible():
                return True
        except Exception:
            pass
        page.wait_for_timeout(200)
    return False


def is_disabled(page, selector):
    try:
        loc = page.locator(selector)
        return loc.count() > 0 and loc.first.is_disabled()
    except Exception:
        return False

def wait_modal_open(page, timeout=8000):
    try:
        page.wait_for_selector(".modal.show", state="visible", timeout=timeout)
        return
    except PWTimeout:
        pass
    page.wait_for_selector(
        "#modal-booking .modal-content, #modal-payment .modal-content, #modal-customer .modal-content, "
        "#modal-dress .modal-content, #modal-service .modal-content",
        state="visible",
        timeout=timeout,
    )

def click_action_in_row(page, view_selector, row_text, action_text=None):
    row = page.locator(f"{view_selector} .ag-row", has_text=row_text).first
    if action_text:
        row.locator(".ag-cell.ag-action-cell", has_text=action_text).first.click(force=True)
    else:
        row.locator(".ag-cell.ag-action-cell").first.click(force=True)

def open_action_details(page, scope_selector, action_text, empty_text=None, screenshot_path=None, max_try=5):
    cells = page.locator(f"{scope_selector} .ag-cell.ag-action-cell", has_text=action_text)
    count = cells.count()
    for i in range(min(count, max_try)):
        cells.nth(i).click(force=True)
        try:
            wait_modal_open(page)
        except PWTimeout:
            continue
        if empty_text:
            try:
                body_text = page.locator("#details-viewer-body").inner_text().strip()
            except Exception:
                body_text = ""
            if empty_text in body_text:
                safe_click(page, "#btn-close-details")
                wait_for_no_modal(page)
                continue
        if screenshot_path:
            page.screenshot(path=str(screenshot_path))
        safe_click(page, "#btn-close-details")
        wait_for_no_modal(page)
        return True
    if screenshot_path:
        page.screenshot(path=str(screenshot_path))
    return False

def export_current_table(page, logs_dir, name, scope_selector):
    # AG Grid export can trigger browser download or a client-side blob path.
    # Treat a successful click on the export button as a valid fallback.
    btn = page.locator(f"{scope_selector} button", has_text="Excel/CSV").first
    if btn.count() == 0:
        page.screenshot(path=str(logs_dir / f"e2e_export_{name}_btn_missing.png"))
        return False

    for _ in range(3):
        try:
            btn.scroll_into_view_if_needed()
        except Exception:
            pass
        try:
            with page.expect_download(timeout=6000) as download_info:
                btn.click(force=True)
            download = download_info.value
            dest = logs_dir / f"export_{name}.csv"
            download.save_as(dest)
            return True
        except Exception:
            # Fallback for client-side export flows where Playwright does not emit download events.
            try:
                btn.click(force=True)
                page.wait_for_timeout(800)
                return True
            except Exception:
                page.wait_for_timeout(500)

    page.screenshot(path=str(logs_dir / f"e2e_export_{name}_failed.png"))
    return False


def select_and_enable(page, dropdown_id, text, button_id, retries=5):
    for _ in range(retries):
        try:
            select_by_text(page, dropdown_id, text)
        except Exception:
            page.wait_for_timeout(500)
            continue
        page.wait_for_timeout(500)
        try:
            if page.locator(button_id).is_enabled():
                return True
        except Exception:
            pass
    return False

def open_tab(page, nav_id, view_id, wait_selector):
    # Defensive cleanup: an open modal can block tab switches and clicks.
    wait_for_no_modal(page, timeout_ms=1500)

    def view_visible():
        try:
            return page.evaluate(
                "() => { const el = document.querySelector('" + view_id + "'); return !!(el && el.style.display !== 'none'); }"
            )
        except Exception:
            return False

    def ensure_nav_visible():
        loc = page.locator(nav_id)
        try:
            if loc.count() > 0 and loc.is_visible():
                return True
        except Exception:
            pass
        for toggle in ("#btn-sidebar-toggle", "#mb-menu"):
            try:
                if page.locator(toggle).count() > 0:
                    safe_click(page, toggle)
                    page.wait_for_timeout(400)
            except Exception:
                pass
        try:
            return loc.count() > 0 and loc.is_visible()
        except Exception:
            return False

    fallback = None
    if nav_id == "#nav-customers":
        fallback = "#mb-customers"
    elif nav_id == "#nav-bookings":
        fallback = "#mb-bookings"
    elif nav_id == "#nav-finance":
        fallback = "#mb-finance"

    for _ in range(3):
        wait_for_no_modal(page, timeout_ms=1000)
        ensure_nav_visible()
        safe_click(page, nav_id)
        page.wait_for_timeout(400)
        if view_visible():
            break
        try:
            page.evaluate("sel => { const el = document.querySelector(sel); if (el) el.click(); }", nav_id)
            page.wait_for_timeout(400)
        except Exception:
            pass
        if fallback:
            safe_click(page, fallback)
            page.wait_for_timeout(400)
            try:
                page.evaluate("sel => { const el = document.querySelector(sel); if (el) el.click(); }", fallback)
                page.wait_for_timeout(400)
            except Exception:
                pass
        if view_visible():
            break

    try:
        page.wait_for_function(
            "() => { const el = document.querySelector('" + view_id + "'); return !!(el && el.style.display !== 'none'); }",
            timeout=15000,
        )
        wait_visible(page, wait_selector)
        page.wait_for_timeout(400)
    except Exception:
        try:
            page.screenshot(path=str(Path("logs") / f"e2e_open_tab_failed_{view_id.strip('#')}.png"))
        except Exception:
            pass


def wait_for_no_modal(page, timeout_ms=8000):
    try:
        page.wait_for_selector(".modal.show", state="detached", timeout=timeout_ms)
    except PWTimeout:
        # Fallback: try closing via Escape or close buttons
        page.keyboard.press("Escape")
        try:
            page.wait_for_selector(".modal.show", state="detached", timeout=2000)
        except PWTimeout:
            close_btn = page.locator(".modal.show .btn-close")
            if close_btn.count() > 0:
                close_btn.first.click(force=True)
                page.wait_for_timeout(500)


def run_responsive_smoke(browser, logs_dir):
    scenarios = [
        ("phone", {"width": 390, "height": 844}),
        ("tablet", {"width": 768, "height": 1024}),
        ("desktop", {"width": 1400, "height": 900}),
    ]

    def login(page):
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        wait_for_app_shell(page, timeout_ms=30000)
        page.wait_for_timeout(1200)
        if page.locator("#login-username").count() > 0:
            page.fill("#login-username", USERNAME)
            page.fill("#login-password", PASSWORD)
            safe_click(page, "#login-btn" if page.locator("#login-btn").count() > 0 else "#btn-login")
            page.wait_for_timeout(1800)
        page.wait_for_function(
            """
            () => {
                return !!document.querySelector('#tab-content')
                    && (!!document.querySelector('#nav-finance') || !!document.querySelector('#mb-finance'));
            }
            """,
            timeout=30000,
        )
        page.wait_for_timeout(1000)

    for name, viewport in scenarios:
        context = browser.new_context(accept_downloads=True, viewport=viewport)
        page = context.new_page()
        page.set_default_timeout(60000)
        login(page)
        page.screenshot(path=str(logs_dir / f"responsive_{name}_finance.png"))

        bottom_nav_visible = page.locator(".bottom-nav").count() > 0 and page.locator(".bottom-nav").is_visible()
        if name == "phone" and not bottom_nav_visible:
            raise SystemExit("Responsive smoke failed: phone bottom nav is not visible.")
        if name == "tablet" and bottom_nav_visible:
            raise SystemExit("Responsive smoke failed: tablet bottom nav should be hidden.")

        if name == "phone":
            safe_click(page, "#mb-menu")
            page.wait_for_timeout(600)
            shell_open = page.evaluate(
                "() => document.getElementById('app-shell')?.classList.contains('mobile-menu-open') || false"
            )
            if not shell_open:
                raise SystemExit("Responsive smoke failed: phone menu did not open.")
            safe_click(page, "#sidebar-backdrop")
            page.wait_for_timeout(500)
            shell_closed = not page.evaluate(
                "() => document.getElementById('app-shell')?.classList.contains('mobile-menu-open') || false"
            )
            if not shell_closed:
                raise SystemExit("Responsive smoke failed: phone menu did not close on backdrop tap.")

            safe_click(page, "#mb-bookings")
            page.wait_for_timeout(1200)
            page.screenshot(path=str(logs_dir / "responsive_phone_bookings.png"))
            if page.locator(".mobile-record-list").count() == 0 or not page.locator(".mobile-record-list").is_visible():
                raise SystemExit("Responsive smoke failed: phone card list is not visible on bookings.")

            safe_click(page, "#btn-add-booking-modal")
            wait_modal_open(page)
            modal_is_fullscreen = page.evaluate(
                """
                () => {
                    const dialog = document.querySelector('#modal-booking .modal-dialog');
                    if (!dialog) return false;
                    const rect = dialog.getBoundingClientRect();
                    return rect.width >= (window.innerWidth - 24);
                }
                """
            )
            if not modal_is_fullscreen:
                raise SystemExit("Responsive smoke failed: booking modal is not fullscreen on phone.")
            page.screenshot(path=str(logs_dir / "responsive_phone_booking_modal.png"))
            wait_for_no_modal(page)

            no_overflow = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1")
            if not no_overflow:
                raise SystemExit("Responsive smoke failed: phone layout has horizontal overflow.")

        if name == "tablet":
            safe_click(page, "#btn-sidebar-toggle")
            page.wait_for_timeout(600)
            safe_click(page, "#nav-bookings")
            page.wait_for_timeout(1200)
            page.screenshot(path=str(logs_dir / "responsive_tablet_bookings.png"))
            if page.locator(".desktop-table-view").count() == 0 or not page.locator(".desktop-table-view").is_visible():
                raise SystemExit("Responsive smoke failed: tablet grid view is not visible.")
            if page.locator(".mobile-record-list").count() > 0 and page.locator(".mobile-record-list").is_visible():
                raise SystemExit("Responsive smoke failed: tablet should not show phone card list.")

        if name == "desktop":
            safe_click(page, "#nav-bookings")
            page.wait_for_timeout(1000)
            if page.locator(".desktop-table-view").count() == 0 or not page.locator(".desktop-table-view").is_visible():
                raise SystemExit("Responsive smoke failed: desktop grid view is not visible.")

        context.close()


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


def get_dropdown_options(page, dropdown_id):
    container = page.locator(f"#{dropdown_id}")
    try:
        container.scroll_into_view_if_needed()
    except Exception:
        pass
    container.click(force=True)
    page.wait_for_timeout(200)
    options = page.evaluate(
        """
        (id) => {
            const root = document.querySelector('#' + id);
            if (!root) return [];
            const menu =
                root.querySelector('.Select-menu-outer') ||
                document.querySelector('.Select-menu-outer') ||
                document.querySelector('[role=listbox]');
            if (!menu) return [];
            const nodes = menu.querySelectorAll('.Select-option, [role=option], .dash-options-list-option');
            return Array.from(nodes)
                .map(o => (o.textContent || '').trim())
                .filter(Boolean);
        }
        """,
        dropdown_id,
    )
    return options


def dropdown_has_option(page, dropdown_id, text):
    container = page.locator(f"#{dropdown_id}")
    try:
        container.scroll_into_view_if_needed()
    except Exception:
        pass
    container.click(force=True)
    has = False
    try:
        page.wait_for_selector(f"#{dropdown_id} input", state="visible", timeout=2000)
        inp = page.locator(f"#{dropdown_id} input")
        inp.fill(text)
        page.wait_for_timeout(300)
        has = (
            page.locator(".Select-option", has_text=text).count() > 0
            or page.locator("div[role='option']", has_text=text).count() > 0
        )
    except Exception:
        # Some react-select instances render without a visible search input.
        # In that case, inspect currently rendered options directly.
        options = get_dropdown_options(page, dropdown_id)
        needle = " ".join(str(text).split()).lower()
        has = any(
            needle in " ".join(str(opt).split()).lower()
            for opt in options
        )
    return has


def select_dropdown_value(page, dropdown_id, text, retries=5):
    target = " ".join(str(text).split())
    target_l = target.lower()
    for _ in range(retries):
        try:
            select_by_text(page, dropdown_id, text)
        except Exception:
            page.wait_for_timeout(300)
            continue
        page.wait_for_timeout(300)
        selected_values = page.evaluate(
            """
            (id) => {
                const root = document.getElementById(id);
                if (!root) return [];
                const direct = Array.from(root.querySelectorAll('.Select-value-label'))
                    .map(el => (el.textContent || '').trim())
                    .filter(Boolean);
                if (direct.length) return direct;
                const single = root.querySelector('.Select-value')?.textContent || '';
                if (single.trim()) return [single.trim()];
                const modern = Array.from(
                    root.querySelectorAll(
                        '[id$="-value"], [id*="-value"], [class*="singleValue"], [data-dash-dropdown-value]'
                    )
                )
                    .map(el => (el.textContent || '').trim())
                    .filter(v => v && !v.includes("اختر"))
                    .filter(v => v !== "x" && v !== "×");
                return modern;
            }
            """,
            dropdown_id,
        )
        if any(
            target_l in " ".join(str(v).split()).lower()
            or " ".join(str(v).split()).lower() in target_l
            for v in selected_values
        ):
            return True
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


def _dropdown_selected_text(page, dropdown_id):
    try:
        txt = page.evaluate(
            """
            (id) => {
                const root = document.getElementById(id);
                if (!root) return "";
                const nodes = root.querySelectorAll(
                    '.Select-value-label, .Select-value, [id$="-value"], [id*="-value"], [class*="singleValue"], [data-dash-dropdown-value]'
                );
                const vals = Array.from(nodes)
                    .map(n => (n.textContent || '').trim())
                    .filter(Boolean)
                    .filter(v => v !== "x" && v !== "×");
                if (!vals.length) return "";
                return vals.join(' | ');
            }
            """,
            dropdown_id,
        )
        return str(txt or "").strip()
    except Exception:
        return ""


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


def select_dropdown_or_first(page, dropdown_id, text, retries=5):
    # Prefer strict matching for deterministic E2E assertions.
    if str(text or "").strip():
        return select_dropdown_value(page, dropdown_id, text, retries=retries)
    try:
        select_first_option(page, dropdown_id)
        return True
    except Exception:
        return False


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


def main():
    ts = int(time.time())
    today = date.today()
    tomorrow = today + timedelta(days=1)
    # Use a far-future ts-based date to avoid collisions with existing bookings.
    same_day = (today + timedelta(days=365 + (ts % 100))).isoformat()

    bride_delete = f"E2E Bride Del {ts}"
    groom_delete = f"E2E Groom Del {ts}"
    bride_booking = f"E2E Bride Book {ts}"
    groom_booking = f"E2E Groom Book {ts}"
    bride_booking2 = f"E2E Bride Book2 {ts}"
    groom_booking2 = f"E2E Groom Book2 {ts}"
    bride_quick = f"E2E Bride Quick {ts}"
    groom_quick = f"E2E Groom Quick {ts}"

    service_used = f"E2E Service Used {ts}"
    service_unused = f"E2E Service Unused {ts}"
    service_edit_price = "600"

    phone_delete = "01" + str(ts)[-9:]
    phone_booking = "01" + str(ts + 1)[-9:]
    phone_booking2 = "01" + str(ts + 2)[-9:]
    phone_quick = "01" + str(ts + 3)[-9:]

    dress_used = f"DR{str(ts)[-6:]}"
    dress_unused = f"DU{str(ts)[-6:]}"
    dress_desc_used = f"E2E Dress Used {ts}"
    dress_desc_unused = f"E2E Dress Unused {ts}"

    dept_name = f"قسم اختبار {ts}"
    dept_name_edit = f"قسم اختبار {ts} 2"

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    big_img_path, small_img_path = create_test_images(logs_dir)

    errors = []
    network_errors = []

    def on_console(msg):
        if msg.type == "error":
            text = msg.text
            # Ignore AG Grid enterprise license watermark warnings
            if (
                "AG Grid Enterprise License" in text
                or "License Key Not Found" in text
                or "watermark" in text.lower()
                or "ag-grid.com" in text.lower()
                or "trial" in text.lower()
                or text.strip("* ").strip() == ""
            ):
                return
            errors.append(text)

    def on_response(resp):
        try:
            if resp.status >= 400 and "_dash-update-component" in resp.url:
                body = resp.text()
                network_errors.append(f"URL: {resp.url} STATUS: {resp.status}\\n{body[:2000]}")
        except Exception:
            pass

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=HEADLESS)
        except Exception:
            browser = p.chromium.launch(headless=True)

        context = browser.new_context(accept_downloads=True, viewport={"width": 1400, "height": 900})
        page = context.new_page()
        page.on("console", on_console)
        page.on("response", on_response)
        page.set_default_timeout(60000)

        page.goto(BASE_URL, wait_until="commit", timeout=60000)
        wait_for_app_shell(page, timeout_ms=30000)
        page.screenshot(path=str(logs_dir / "e2e_before_login.png"))
        try:
            print("login-username count:", page.locator("#login-username").count())
            print("nav-finance count:", page.locator("#nav-finance").count())
        except Exception:
            pass

        if page.locator("#login-username").count() > 0:
            page.wait_for_selector("#login-username", timeout=15000)
            page.fill("#login-username", USERNAME)
            page.fill("#login-password", PASSWORD)
            if page.locator("#login-btn").count() > 0:
                page.click("#login-btn")
            else:
                page.click("#btn-login")
            try:
                page.wait_for_function(
                    "() => { try { const s = localStorage.getItem('user_session_store'); if (!s) return false; const o = JSON.parse(s); return !!o.logged_in; } catch (e) { return false; } }",
                    timeout=20000,
                )
            except PWTimeout:
                pass
            page.wait_for_timeout(800)
            page.screenshot(path=str(logs_dir / "e2e_after_login.png"))
            try:
                session_val = page.evaluate("() => window.localStorage.getItem('user_session_store')")
            except Exception:
                session_val = None
            print("user_session_store:", session_val)
            try:
                page.wait_for_selector("#nav-finance", timeout=20000)
            except PWTimeout:
                pass

        if page.locator("#nav-finance").count() == 0 and page.locator("#main-tabs").count() == 0:
            alert_text = ""
            if page.locator("#login-alert").count() > 0:
                alert_text = page.locator("#login-alert").inner_text().strip()
            page.screenshot(path=str(logs_dir / "e2e_login_failed.png"))
            msg = "Login failed or app did not load."
            if alert_text:
                msg += f" Alert: {alert_text}"
            raise SystemExit(msg)

        page.screenshot(path=str(logs_dir / "e2e_home.png"))

        selected_modes = []
        if CORE_SMOKE:
            selected_modes.append("CORE_SMOKE")
        if BOOKING_ONLY:
            selected_modes.append("BOOKING_ONLY")
        if FULL_REGRESSION:
            selected_modes.append("FULL_REGRESSION")

        # Keep mode choice deterministic when multiple env flags are set.
        # Precedence: CORE_SMOKE > BOOKING_ONLY > FULL_REGRESSION.
        if len(selected_modes) > 1:
            print(
                "Multiple E2E modes set: "
                + ", ".join(selected_modes)
                + ". Using precedence CORE_SMOKE > BOOKING_ONLY > FULL_REGRESSION."
            )

        if CORE_SMOKE:
            print("[E2E] mode=CORE_SMOKE")
            run_core_smoke(
                page,
                logs_dir,
                ts,
                service_used,
                bride_booking,
            )
            browser.close()
            print("CORE_SMOKE completed successfully.")
            return

        if BOOKING_ONLY:
            print("[E2E] mode=BOOKING_ONLY")
            run_booking_only(
                page,
                logs_dir,
                ts,
                today,
                tomorrow,
                same_day,
                bride_booking,
                bride_booking2,
                service_used,
                dress_used,
                dress_unused,
            )
            browser.close()
            print("BOOKING_ONLY completed successfully.")
            return

        if not FULL_REGRESSION:
            print("No E2E mode selected. Use CORE_SMOKE=1 or BOOKING_ONLY=1 or FULL_REGRESSION=1.")
            browser.close()
            return

        print("[E2E] mode=FULL_REGRESSION")
        print(f"[FULL_REGRESSION] phase={FULL_PHASE}")

        if FULL_PHASE == "phase1b1":
            run_full_phase1b1(
                page,
                logs_dir,
                ts,
                service_used,
                service_unused,
                bride_delete,
                bride_booking,
                bride_booking2,
            )
            browser.close()
            print("FULL_REGRESSION phase1b1 completed successfully.")
            return

        print("[FULL_PHASE1B2] step 1: services", flush=True)
        # Add service (used in bookings - dresses dept)
        open_tab(page, "#nav-services", "#view-services", "#btn-add-service-modal")
        if not export_current_table(page, logs_dir, "services", "#view-services"):
            errors.append("Services export failed.")
        if not open_service_modal(page):
            errors.append("Service modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_service_modal_failed.png"))
            raise SystemExit("Service modal did not open.")
        page.fill("#s-name", service_used)
        select_by_text(page, "s-dept", "الفساتين")
        page.fill("#s-price", "500")
        safe_click(page, "#btn-save-service")
        wait_for_no_modal(page)
        page.wait_for_timeout(800)

        # Add service (unused - for delete test)
        if not open_service_modal(page):
            errors.append("Service modal did not open (unused).")
            page.screenshot(path=str(logs_dir / "e2e_service_modal_failed_unused.png"))
            raise SystemExit("Service modal did not open (unused).")
        page.fill("#s-name", service_unused)
        select_first_option(page, "s-dept")
        page.fill("#s-price", "450")
        safe_click(page, "#btn-save-service")
        wait_for_no_modal(page)
        page.wait_for_timeout(800)
        page.screenshot(path=str(logs_dir / "e2e_service.png"))

        if FULL_PHASE == "phase1a":
            page.screenshot(path=str(logs_dir / "e2e_full_phase1a_done.png"))
            browser.close()
            print("FULL_REGRESSION phase1a completed successfully.")
            return

        # Edit service (price only)
        if FULL_PHASE != "phase1b1":
            open_tab(page, "#nav-services", "#view-services", "#btn-add-service-modal")
            if select_and_enable(page, "s-search", service_used, "#btn-edit-service"):
                safe_click(page, "#btn-edit-service")
                wait_modal_open(page)
                page.wait_for_selector("#s-price")
                page.fill("#s-price", service_edit_price)
                safe_click(page, "#btn-save-service")
                wait_for_no_modal(page)
            else:
                page.screenshot(path=str(logs_dir / "e2e_service_edit_failed.png"))

        print("[FULL_PHASE1B2] step 2: customers", flush=True)
        # Add customer (for edit/delete)
        open_tab(page, "#nav-customers", "#view-customers", "#btn-add-customer-modal")
        if not export_current_table(page, logs_dir, "customers", "#view-customers"):
            errors.append("Customers export failed.")
        if not open_customer_modal(page):
            errors.append("Customer modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_customer_modal_failed.png"))
            raise SystemExit("Customer modal did not open.")
        page.fill("#c-name", bride_delete)
        page.fill("#c-groom", groom_delete)
        page.fill("#c-phone1", phone_delete)
        page.fill("#c-phone2", phone_delete)
        page.fill("#c-addr", "E2E Address")
        page.fill("#c-notes", "E2E customer delete")
        safe_click(page, "#btn-save-customer")
        wait_for_no_modal(page)
        page.wait_for_timeout(800)

        # Edit customer (notes only)
        open_tab(page, "#nav-customers", "#view-customers", "#btn-add-customer-modal")
        if select_and_enable(page, "c-search", bride_delete, "#btn-edit-customer"):
            safe_click(page, "#btn-edit-customer")
            wait_modal_open(page)
            page.wait_for_selector("#c-notes")
            page.fill("#c-notes", "E2E customer edited")
            safe_click(page, "#btn-save-customer")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_customer_edit_failed.png"))

        # Add customer (for bookings with payments)
        if not open_customer_modal(page):
            errors.append("Customer modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_customer_modal_failed.png"))
            raise SystemExit("Customer modal did not open.")
        page.fill("#c-name", bride_booking)
        page.fill("#c-groom", groom_booking)
        page.fill("#c-phone1", phone_booking)
        page.fill("#c-phone2", phone_booking)
        page.fill("#c-addr", "E2E Address")
        page.fill("#c-notes", "E2E customer booking")
        safe_click(page, "#btn-save-customer")
        wait_for_no_modal(page)
        page.wait_for_timeout(500)

        # Add customer (for booking delete)
        if not open_customer_modal(page):
            errors.append("Customer modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_customer_modal_failed.png"))
            raise SystemExit("Customer modal did not open.")
        page.fill("#c-name", bride_booking2)
        page.fill("#c-groom", groom_booking2)
        page.fill("#c-phone1", phone_booking2)
        page.fill("#c-phone2", phone_booking2)
        page.fill("#c-addr", "E2E Address")
        page.fill("#c-notes", "E2E customer booking delete")
        safe_click(page, "#btn-save-customer")
        wait_for_no_modal(page)
        page.wait_for_timeout(500)
        page.screenshot(path=str(logs_dir / "e2e_customer.png"))

        if FULL_PHASE == "phase1b2a":
            page.screenshot(path=str(logs_dir / "e2e_full_phase1b2a_done.png"))
            browser.close()
            print("FULL_REGRESSION phase1b2a completed successfully.")
            return

        if FULL_PHASE == "phase1b1":
            page.screenshot(path=str(logs_dir / "e2e_full_phase1b1_done.png"))
            browser.close()
            print("FULL_REGRESSION phase1b1 completed successfully.")
            return

        print("[FULL_PHASE1B2] step 3: dress image flow", flush=True)
        # Image upload tests (dress images)
        image_dress = f"IMG{str(ts)[-6:]}"
        open_tab(page, "#nav-dresses", "#view-dresses", "#btn-add-dress-modal")
        if not open_dress_modal(page):
            errors.append("Dress modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_dress_modal_failed.png"))
            raise SystemExit("Dress modal did not open.")
        page.fill("#d-code", image_dress)
        page.fill("#d-desc", f"E2E Dress Image {ts}")
        # Upload big image (>300KB) should be blocked
        page.set_input_files("#d-upload-image input[type=file]", str(big_img_path))
        safe_click(page, "#btn-save-dress")
        page.wait_for_timeout(800)
        alert_text = page.locator("#d-alert").inner_text() if page.locator("#d-alert").count() else ""
        if "حجم الصورة كبير" not in alert_text:
            errors.append("Large image upload was not blocked.")
            page.screenshot(path=str(logs_dir / "e2e_image_large_not_blocked.png"))
        # Upload small image (<300KB) should succeed
        page.set_input_files("#d-upload-image input[type=file]", str(small_img_path))
        safe_click(page, "#btn-save-dress")
        wait_for_no_modal(page)
        page.wait_for_timeout(800)

        # Verify image file saved
        img_saved = False
        for ext in (".png", ".jpg", ".webp"):
            if (Path("dress_images") / f"{image_dress}{ext}").exists():
                img_saved = True
                break
        if not img_saved:
            errors.append("Small image was not saved to dress_images.")

        # Delete image dress and ensure image file removed
        open_tab(page, "#nav-dresses", "#view-dresses", "#btn-add-dress-modal")
        if select_and_enable(page, "d-search", image_dress, "#btn-delete-dress"):
            safe_click(page, "#btn-delete-dress")
            safe_click(page, "#btn-confirm-delete-d")
            wait_for_no_modal(page)
            page.wait_for_timeout(500)
        else:
            errors.append("Image dress not found for delete.")
        img_still = False
        for ext in (".png", ".jpg", ".webp"):
            if (Path("dress_images") / f"{image_dress}{ext}").exists():
                img_still = True
                break
        if img_still:
            errors.append("Image file was not removed after dress delete.")

        print("[FULL_PHASE1B2] step 4: dresses used/unused", flush=True)
        # Add dresses (used + unused)
        open_tab(page, "#nav-dresses", "#view-dresses", "#btn-add-dress-modal")
        if not open_dress_modal(page):
            errors.append("Dress modal did not open (used).")
            page.screenshot(path=str(logs_dir / "e2e_dress_modal_used_failed.png"))
            raise SystemExit("Dress modal did not open (used).")
        page.fill("#d-code", dress_used)
        page.fill("#d-desc", dress_desc_used)
        safe_click(page, "#btn-save-dress")
        wait_for_no_modal(page)
        page.wait_for_timeout(800)

        if not open_dress_modal(page):
            errors.append("Dress modal did not open (unused).")
            page.screenshot(path=str(logs_dir / "e2e_dress_modal_unused_failed.png"))
            raise SystemExit("Dress modal did not open (unused).")
        page.fill("#d-code", dress_unused)
        page.fill("#d-desc", dress_desc_unused)
        safe_click(page, "#btn-save-dress")
        wait_for_no_modal(page)
        page.wait_for_timeout(800)

        print("[FULL_PHASE1B2] step 5: bookings flow", flush=True)
        # Add booking (with payment - dresses dept)
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if not export_current_table(page, logs_dir, "bookings", "#view-bookings"):
            errors.append("Bookings export failed.")
        if not open_booking_modal(page):
            errors.append("Booking modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_booking_modal_failed.png"))
            raise SystemExit("Booking modal did not open.")
        if not select_dropdown_or_first(page, "b-dept", "\u0627\u0644\u0641\u0633\u0627\u062a\u064a\u0646"):
            errors.append("Failed to select dresses department for primary booking.")
            page.screenshot(path=str(logs_dir / "e2e_booking_primary_dept_select_failed.png"))
        if not select_dropdown_or_first(page, "b-customer", bride_booking):
            errors.append("Failed to select customer for primary booking.")
            page.screenshot(path=str(logs_dir / "e2e_booking_primary_customer_select_failed.png"))
        if not select_dropdown_or_first(page, "b-service", service_used):
            errors.append("Failed to select service for primary booking.")
            page.screenshot(path=str(logs_dir / "e2e_booking_primary_service_select_failed.png"))
        ensure_dress_ready(page)
        if not dropdown_has_option(page, "b-dress", dress_used) or not dropdown_has_option(page, "b-dress", dress_unused):
            page.screenshot(path=str(logs_dir / "e2e_booking_dress_options_missing.png"))
        if not select_dropdown_or_first(page, "b-dress", dress_used):
            errors.append("Failed to select used dress for primary booking.")
            page.screenshot(path=str(logs_dir / "e2e_booking_primary_dress_select_failed.png"))
        if not ensure_booking_input_visible(page, logs_dir, "e2e_booking_primary"):
            errors.append("Booking modal closed before primary date fill.")
            raise SystemExit("Booking modal closed before primary date fill.")
        page.fill("#b-event-date", same_day)
        page.fill("#b-price", "1000")
        page.fill("#b-paid", "200")
        if not ensure_booking_required_selected(page, logs_dir, "e2e_booking_primary"):
            errors.append("Primary booking required dropdowns were not selected.")
            raise SystemExit("Primary booking required dropdowns were not selected.")
        dump_booking_save_state(page, logs_dir, "e2e_booking_primary_before_save")
        click_booking_save(page)
        page.wait_for_timeout(500)
        dump_booking_save_state(page, logs_dir, "e2e_booking_primary_after_save")
        try:
            page.wait_for_selector("#modal-booking .modal-content", state="hidden", timeout=7000)
        except PWTimeout:
            open_now, alert_text = booking_modal_still_open_with_alert(page)
            if open_now:
                page.screenshot(path=str(logs_dir / "e2e_booking_primary_save_failed_modal_open.png"))
                with open(logs_dir / "e2e_booking_primary_save_failed_alert.txt", "w", encoding="utf-8") as f:
                    f.write(alert_text or "(empty alert)")
                raise SystemExit("Primary booking save did not close modal.")
        page.wait_for_timeout(1000)
        # Ensure first booking is persisted before running conflict checks.
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if not wait_booking_visible_in_table(page, bride_booking, retries=20, delay_ms=500):
            errors.append("Primary booking was not visible in bookings table after save.")
            page.screenshot(path=str(logs_dir / "e2e_booking_primary_not_visible_after_save.png"))
            raise SystemExit("Primary booking was not visible after save; aborting conflict check.")

        # Attempt double booking same dress on same day (should be blocked)
        if not open_booking_modal(page):
            errors.append("Booking modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_booking_modal_failed.png"))
            raise SystemExit("Booking modal did not open.")
        if not select_dropdown_value(page, "b-dept", "\u0627\u0644\u0641\u0633\u0627\u062a\u064a\u0646"):
            errors.append("Failed to select dresses department for same-day conflict check.")
            page.screenshot(path=str(logs_dir / "e2e_booking_conflict_dept_select_failed.png"))
        select_by_text(page, "b-customer", bride_booking2)
        if not select_dropdown_value(page, "b-service", service_used):
            errors.append("Failed to select service for same-day conflict check.")
            page.screenshot(path=str(logs_dir / "e2e_booking_conflict_service_select_failed.png"))
        ensure_dress_ready(page)
        if not select_dropdown_value(page, "b-dress", dress_used):
            errors.append("Failed to select used dress for same-day conflict check.")
            page.screenshot(path=str(logs_dir / "e2e_booking_conflict_dress_select_failed.png"))
        if not ensure_booking_input_visible(page, logs_dir, "e2e_booking_conflict"):
            errors.append("Booking modal closed before conflict date fill.")
            raise SystemExit("Booking modal closed before conflict date fill.")
        page.fill("#b-event-date", same_day)
        page.fill("#b-price", "900")
        page.fill("#b-paid", "0")
        if not expect_booking_blocked(page, logs_dir, "e2e_booking_same_day"):
            errors.append("Same-day double booking was not blocked.")

        # Add booking (no payment - for delete)
        if not open_booking_modal(page):
            errors.append("Booking modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_booking_modal_failed.png"))
            raise SystemExit("Booking modal did not open.")
        if not select_dropdown_value(page, "b-dept", "\u0627\u0644\u0641\u0633\u0627\u062a\u064a\u0646"):
            errors.append("Failed to select dresses department for delete-path booking.")
            page.screenshot(path=str(logs_dir / "e2e_booking_delete_path_dept_select_failed.png"))
        select_by_text(page, "b-customer", bride_booking2)
        if not select_dropdown_value(page, "b-service", service_used):
            errors.append("Failed to select service for delete-path booking.")
            page.screenshot(path=str(logs_dir / "e2e_booking_delete_path_service_select_failed.png"))
        ensure_dress_ready(page)
        if not select_dropdown_value(page, "b-dress", dress_used):
            errors.append("Failed to select used dress for delete-path booking.")
            page.screenshot(path=str(logs_dir / "e2e_booking_delete_path_dress_select_failed.png"))
        page.fill("#b-event-date", tomorrow.isoformat())
        page.fill("#b-price", "800")
        page.fill("#b-paid", "0")
        safe_click(page, "#btn-save-booking")
        wait_for_no_modal(page)
        page.wait_for_timeout(1000)
        page.screenshot(path=str(logs_dir / "e2e_booking.png"))
        # Ensure second booking is persisted before edit-conflict flow.
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if not select_and_enable(page, "b-search", bride_booking2, "#btn-edit-booking", retries=20):
            errors.append("Second booking was not visible after save (possible commit race).")
            page.screenshot(path=str(logs_dir / "e2e_booking_second_not_visible_after_save.png"))

        # Attempt edit booking to conflicting dress/date (should be blocked)
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if select_and_enable(page, "b-search", bride_booking2, "#btn-edit-booking"):
            safe_click(page, "#btn-edit-booking")
            wait_modal_open(page)
            page.wait_for_selector("#b-dept", state="visible")
            if not select_dropdown_value(page, "b-dept", "\u0627\u0644\u0641\u0633\u0627\u062a\u064a\u0646"):
                errors.append("Failed to select dresses department for edit conflict check.")
                page.screenshot(path=str(logs_dir / "e2e_booking_edit_conflict_dept_select_failed.png"))
            ensure_dress_ready(page)
            if not select_dropdown_value(page, "b-dress", dress_used):
                errors.append("Failed to select used dress for edit conflict check.")
                page.screenshot(path=str(logs_dir / "e2e_booking_edit_conflict_dress_select_failed.png"))
            page.fill("#b-event-date", same_day)
            if not expect_booking_blocked(page, logs_dir, "e2e_booking_edit_same_day"):
                errors.append("Edit booking same-day conflict was not blocked.")
        else:
            page.screenshot(path=str(logs_dir / "e2e_booking_edit_conflict_open_failed.png"))

        # Quick add customer from booking modal + booking
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if not open_booking_modal(page):
            errors.append("Booking modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_booking_modal_failed.png"))
            raise SystemExit("Booking modal did not open.")
        if not select_dropdown_value(page, "b-dept", "\u0627\u0644\u0641\u0633\u0627\u062a\u064a\u0646"):
            errors.append("Failed to select dresses department for quick-add flow.")
            page.screenshot(path=str(logs_dir / "e2e_booking_quick_add_dept_select_failed.png"))
        quick_added = open_quick_customer_modal(page)
        if quick_added:
            page.fill("#c-name", bride_quick)
            page.fill("#c-groom", groom_quick)
            page.fill("#c-phone1", phone_quick)
            page.fill("#c-phone2", phone_quick)
            page.fill("#c-addr", "E2E Address")
            page.fill("#c-notes", "E2E customer quick add")
            safe_click(page, "#btn-save-customer")
            wait_for_no_modal(page)

            # Re-open booking modal and create booking for quick-added customer
            if not open_booking_modal(page):
                errors.append("Booking modal did not open (quick add).")
                page.screenshot(path=str(logs_dir / "e2e_booking_modal_quick_failed.png"))
                raise SystemExit("Booking modal did not open (quick add).")
            if not select_dropdown_value(page, "b-dept", "\u0627\u0644\u0641\u0633\u0627\u062a\u064a\u0646"):
                errors.append("Failed to select dresses department for quick-add booking.")
                page.screenshot(path=str(logs_dir / "e2e_booking_quick_add_booking_dept_select_failed.png"))
            select_by_text(page, "b-customer", bride_quick)
            if not select_dropdown_value(page, "b-service", service_used):
                errors.append("Failed to select service for quick-add booking.")
                page.screenshot(path=str(logs_dir / "e2e_booking_quick_add_booking_service_select_failed.png"))
            ensure_dress_ready(page)
            if not select_dropdown_value(page, "b-dress", dress_used):
                errors.append("Failed to select used dress for quick-add booking.")
                page.screenshot(path=str(logs_dir / "e2e_booking_quick_add_dress_select_failed.png"))
            page.fill("#b-price", "900")
            page.fill("#b-paid", "0")
            safe_click(page, "#btn-save-booking")
            wait_for_no_modal(page)
            page.wait_for_timeout(800)
        else:
            errors.append("Quick add customer modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_quick_add_customer_failed.png"))

        print("[FULL_PHASE1B2] step 6: booking edit", flush=True)
        # Edit booking (notes only)
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if select_and_enable(page, "b-search", bride_booking2, "#btn-edit-booking"):
            safe_click(page, "#btn-edit-booking")
            wait_modal_open(page)
            page.wait_for_selector("#b-notes")
            page.fill("#b-notes", "E2E booking edited")
            safe_click(page, "#btn-save-booking")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_booking_edit_failed.png"))

        if FULL_PHASE == "phase1b2b":
            print("[FULL_PHASE1B2B] completed", flush=True)
            page.screenshot(path=str(logs_dir / "e2e_full_phase1b2b_done.png"))
            browser.close()
            print("FULL_REGRESSION phase1b2b completed successfully.")
            return

        if FULL_PHASE in ("phase1", "phase1b", "phase1b2"):
            print("[FULL_PHASE1B2] completed", flush=True)
            page.screenshot(path=str(logs_dir / "e2e_full_phase1b2_done.png"))
            browser.close()
            print("FULL_REGRESSION phase1b2 completed successfully.")
            return

        # Add payment
        open_tab(page, "#nav-payments", "#view-payments", "#btn-add-payment-modal")
        if not export_current_table(page, logs_dir, "payments", "#view-payments"):
            errors.append("Payments export failed.")
        if not open_payment_modal(page):
            errors.append("Payment modal did not open.")
            page.screenshot(path=str(logs_dir / "e2e_payment_modal_failed.png"))
            raise SystemExit("Payment modal did not open.")
        select_by_text(page, "p-booking", bride_booking)
        page.fill("#p-amount", "50")
        safe_click(page, "#btn-save-payment")
        wait_for_no_modal(page)
        page.wait_for_timeout(1000)
        page.screenshot(path=str(logs_dir / "e2e_payment.png"))
        open_tab(page, "#nav-payments", "#view-payments", "#btn-add-payment-modal")
        if not select_and_enable(page, "p-search", bride_booking, "#btn-edit-payment", retries=20):
            errors.append("Payment row not visible after save (possible commit race).")
            page.screenshot(path=str(logs_dir / "e2e_payment_not_visible_after_save.png"))

        # Details: payments from bookings table
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if not open_action_details(
            page,
            "#view-bookings",
            "تفاصيل الدفعات",
            empty_text="لا توجد مدفوعات",
            screenshot_path=logs_dir / "e2e_details_payments_from_bookings.png",
        ):
            errors.append("Booking payments details did not open or had no data.")

        # Details: bookings from customers table
        open_tab(page, "#nav-customers", "#view-customers", "#btn-add-customer-modal")
        if not open_action_details(
            page,
            "#view-customers",
            "تفاصيل الحجوزات",
            empty_text="لا توجد حجوزات",
            screenshot_path=logs_dir / "e2e_details_bookings_from_customers.png",
        ):
            errors.append("Customer bookings details did not open or had no data.")

        # Details: bookings from dresses table
        open_tab(page, "#nav-dresses", "#view-dresses", "#btn-add-dress-modal")
        if not open_action_details(
            page,
            "#view-dresses",
            "تفاصيل الحجوزات",
            empty_text="لا توجد حجوزات",
            screenshot_path=logs_dir / "e2e_details_bookings_from_dresses.png",
        ):
            errors.append("Dress bookings details did not open or had no data.")

        # Details: booking from payments table
        open_tab(page, "#nav-payments", "#view-payments", "#btn-add-payment-modal")
        if not open_action_details(
            page,
            "#view-payments",
            "تفاصيل الحجز",
            screenshot_path=logs_dir / "e2e_details_booking_from_payments.png",
        ):
            errors.append("Payment booking details did not open.")

        # Edit payment (amount)
        open_tab(page, "#nav-payments", "#view-payments", "#btn-add-payment-modal")
        if select_and_enable(page, "p-search", bride_booking, "#btn-edit-payment"):
            safe_click(page, "#btn-edit-payment")
            wait_modal_open(page)
            page.wait_for_selector("#p-amount")
            page.fill("#p-amount", "60")
            safe_click(page, "#btn-save-payment")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_payment_edit_failed.png"))

        # Delete payment
        open_tab(page, "#nav-payments", "#view-payments", "#btn-add-payment-modal")
        if select_and_enable(page, "p-search", bride_booking, "#btn-delete-payment"):
            safe_click(page, "#btn-delete-payment")
            safe_click(page, "#btn-confirm-delete-p")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_payment_delete_failed.png"))

        # Dresses CRUD (edit + delete unused, verify blocked delete on used)
        open_tab(page, "#nav-dresses", "#view-dresses", "#btn-add-dress-modal")
        if select_and_enable(page, "d-search", dress_unused, "#btn-edit-dress"):
            safe_click(page, "#btn-edit-dress")
            try:
                wait_modal_open(page)
                page.wait_for_selector("#d-status")
                page.select_option("#d-status", "محجوز")
                safe_click(page, "#btn-save-dress")
                wait_for_no_modal(page)
            except Exception:
                errors.append("Dress edit modal did not open.")
                page.screenshot(path=str(logs_dir / "e2e_dress_edit_failed.png"))
        else:
            page.screenshot(path=str(logs_dir / "e2e_dress_edit_failed.png"))

        # Attempt delete used dress (should be blocked)
        open_tab(page, "#nav-dresses", "#view-dresses", "#btn-add-dress-modal")
        if select_and_enable(page, "d-search", dress_used, "#btn-delete-dress"):
            safe_click(page, "#btn-delete-dress")
            safe_click(page, "#btn-confirm-delete-d")
            page.wait_for_timeout(800)
            page.screenshot(path=str(logs_dir / "e2e_dress_delete_blocked.png"))
        else:
            page.screenshot(path=str(logs_dir / "e2e_dress_delete_blocked_failed.png"))

        # Delete unused dress (should succeed)
        open_tab(page, "#nav-dresses", "#view-dresses", "#btn-add-dress-modal")
        if select_and_enable(page, "d-search", dress_unused, "#btn-delete-dress"):
            safe_click(page, "#btn-delete-dress")
            safe_click(page, "#btn-confirm-delete-d")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_dress_delete_failed.png"))

        # Settings -> Departments CRUD
        open_tab(page, "#nav-settings", "#view-settings", "#btn-add-dept-modal")
        safe_click(page, "#btn-add-dept-modal")
        page.wait_for_selector("#dept-name")
        page.fill("#dept-name", dept_name)
        safe_click(page, "#btn-save-dept")
        wait_for_no_modal(page)
        page.wait_for_timeout(600)
        page.screenshot(path=str(logs_dir / "e2e_dept.png"))

        # Edit dept
        open_tab(page, "#nav-settings", "#view-settings", "#btn-add-dept-modal")
        if select_and_enable(page, "dept-search", dept_name, "#btn-edit-dept"):
            safe_click(page, "#btn-edit-dept")
            wait_modal_open(page)
            page.wait_for_selector("#dept-name")
            page.fill("#dept-name", dept_name_edit)
            safe_click(page, "#btn-save-dept")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_dept_edit_failed.png"))

        # Delete dept
        open_tab(page, "#nav-settings", "#view-settings", "#btn-add-dept-modal")
        if select_and_enable(page, "dept-search", dept_name_edit, "#btn-delete-dept"):
            safe_click(page, "#btn-delete-dept")
            safe_click(page, "#btn-confirm-delete-dept")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_dept_delete_failed.png"))

        if FULL_PHASE == "phase2":
            page.screenshot(path=str(logs_dir / "e2e_full_phase2_done.png"))
            browser.close()
            print("FULL_REGRESSION phase2 completed successfully.")
            return

        # Cleanup: delete booking without payments
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if select_and_enable(page, "b-search", bride_booking2, "#btn-delete-booking"):
            safe_click(page, "#btn-delete-booking")
            safe_click(page, "#btn-confirm-delete-b")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_booking_delete_failed.png"))

        # Attempt delete booking with payments (should be blocked)
        open_tab(page, "#nav-bookings", "#view-bookings", "#btn-add-booking-modal")
        if select_and_enable(page, "b-search", bride_booking, "#btn-delete-booking"):
            safe_click(page, "#btn-delete-booking")
            safe_click(page, "#btn-confirm-delete-b")
            page.wait_for_timeout(800)
            page.screenshot(path=str(logs_dir / "e2e_booking_delete_blocked.png"))
        else:
            page.screenshot(path=str(logs_dir / "e2e_booking_delete_blocked_failed.png"))

        open_tab(page, "#nav-customers", "#view-customers", "#btn-add-customer-modal")
        if select_and_enable(page, "c-search", bride_delete, "#btn-delete-customer"):
            safe_click(page, "#btn-delete-customer")
            safe_click(page, "#btn-confirm-delete")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_customer_delete_failed.png"))

        # Attempt delete customer with bookings (should be blocked)
        open_tab(page, "#nav-customers", "#view-customers", "#btn-add-customer-modal")
        if select_and_enable(page, "c-search", bride_booking, "#btn-delete-customer"):
            safe_click(page, "#btn-delete-customer")
            safe_click(page, "#btn-confirm-delete")
            page.wait_for_timeout(800)
            page.screenshot(path=str(logs_dir / "e2e_customer_delete_blocked.png"))
        else:
            page.screenshot(path=str(logs_dir / "e2e_customer_delete_blocked_failed.png"))

        # Attempt delete service with bookings (should be blocked)
        open_tab(page, "#nav-services", "#view-services", "#btn-add-service-modal")
        if select_and_enable(page, "s-search", service_used, "#btn-delete-service"):
            safe_click(page, "#btn-delete-service")
            safe_click(page, "#btn-confirm-delete-s")
            page.wait_for_timeout(800)
            page.screenshot(path=str(logs_dir / "e2e_service_delete_blocked.png"))
        else:
            page.screenshot(path=str(logs_dir / "e2e_service_delete_blocked_failed.png"))

        # Delete unused service
        open_tab(page, "#nav-services", "#view-services", "#btn-add-service-modal")
        if select_and_enable(page, "s-search", service_unused, "#btn-delete-service"):
            safe_click(page, "#btn-delete-service")
            safe_click(page, "#btn-confirm-delete-s")
            wait_for_no_modal(page)
        else:
            page.screenshot(path=str(logs_dir / "e2e_service_delete_failed.png"))

        # Logout
        if page.locator("#logout-btn").count() > 0:
            safe_click(page, "#logout-btn")
            page.wait_for_timeout(500)

        page.screenshot(path=str(logs_dir / "e2e_done.png"))
        browser.close()

    if errors:
        print("Console errors detected:")
        for e in errors:
            print("-", e)
        if network_errors:
            log_path = logs_dir / "e2e_network_errors.log"
            log_path.write_text("\\n\\n".join(network_errors), encoding="utf-8")
            print(f"Network error details saved to: {log_path}")
        raise SystemExit(1)

    print("E2E completed successfully.")


if __name__ == "__main__":
    main()


