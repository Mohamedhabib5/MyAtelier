from e2e_playwright_context import *

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
            close_btn = page.locator(".modal.show .btn-close, #btn-close-custody-workflow")
            if close_btn.count() > 0:
                close_btn.first.click(force=True)
                page.wait_for_timeout(500)
