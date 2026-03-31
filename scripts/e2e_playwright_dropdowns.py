from e2e_playwright_context import *
from e2e_playwright_navigation import select_by_text

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
    if not target:
        return False
    selected_text = " ".join(_dropdown_selected_text(page, dropdown_id).split()).lower()
    if selected_text and (target_l in selected_text or selected_text in target_l):
        return True
    for _ in range(retries):
        try:
            select_by_text(page, dropdown_id, text)
        except Exception:
            page.wait_for_timeout(300)
            continue
        page.wait_for_timeout(300)
        selected_text = " ".join(_dropdown_selected_text(page, dropdown_id).split()).lower()
        if selected_text and (target_l in selected_text or selected_text in target_l):
            return True
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

def select_dropdown_or_first(page, dropdown_id, text, retries=5):
    # Prefer strict matching for deterministic E2E assertions.
    if str(text or "").strip():
        return select_dropdown_value(page, dropdown_id, text, retries=retries)
    try:
        select_first_option(page, dropdown_id)
        return True
    except Exception:
        return False
