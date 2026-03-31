from e2e_playwright_context import *
from e2e_playwright_helpers import *

def run_responsive_smoke(browser, logs_dir):
    scenarios = [
        ("phone", {"width": 390, "height": 844}),
        ("tablet", {"width": 768, "height": 1024}),
        ("desktop", {"width": 1400, "height": 900}),
    ]

    def tap(page, selector):
        page.locator(selector).first.click(force=True)

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
        page.wait_for_selector("#kpi-income", state="visible", timeout=30000)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(logs_dir / f"responsive_{name}_finance.png"))

        bottom_nav_visible = page.locator(".bottom-nav").count() > 0 and page.locator(".bottom-nav").is_visible()
        if name == "phone" and not bottom_nav_visible:
            raise SystemExit("Responsive smoke failed: phone bottom nav is not visible.")
        if name == "tablet" and bottom_nav_visible:
            raise SystemExit("Responsive smoke failed: tablet bottom nav should be hidden.")

        if name == "phone":
            tap(page, "#mb-menu")
            try:
                page.wait_for_function(
                    "() => document.getElementById('app-shell')?.classList.contains('mobile-menu-open') || false",
                    timeout=6000,
                )
                page.wait_for_selector("#sidebar-backdrop.show", state="visible", timeout=6000)
                page.wait_for_timeout(250)
            except PWTimeout:
                raise SystemExit("Responsive smoke failed: phone menu did not open.")

            # Click the exposed left side of the backdrop area, not the element center under the sidebar.
            page.mouse.click(20, min(250, max(120, viewport["height"] // 2)))
            try:
                page.wait_for_function(
                    "() => !(document.getElementById('app-shell')?.classList.contains('mobile-menu-open') || false)",
                    timeout=6000,
                )
                page.wait_for_function(
                    "() => !(document.getElementById('sidebar-backdrop')?.classList.contains('show') || false)",
                    timeout=6000,
                )
                page.wait_for_timeout(800)
            except PWTimeout:
                raise SystemExit("Responsive smoke failed: phone menu did not close on outside tap.")

            tap(page, "#mb-bookings")
            page.wait_for_timeout(1200)
            page.screenshot(path=str(logs_dir / "responsive_phone_bookings.png"))
            phone_bookings_list = page.locator("#bookings-table-container .mobile-record-list").first
            if phone_bookings_list.count() == 0 or not phone_bookings_list.is_visible():
                raise SystemExit("Responsive smoke failed: phone card list is not visible on bookings.")

            safe_click(page, "#btn-add-booking-modal")
            wait_modal_open(page)
            modal_is_fullscreen = page.evaluate(
                """
                () => {
                    const dialog = document.querySelector('.form-modal.modal.show .modal-dialog');
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
            page.wait_for_function(
                "() => document.getElementById('app-shell')?.classList.contains('mobile-menu-open') || false",
                timeout=6000,
            )
            page.wait_for_selector("#sidebar-backdrop.show", state="visible", timeout=6000)
            safe_click(page, "#nav-bookings")
            page.wait_for_timeout(1200)
            page.screenshot(path=str(logs_dir / "responsive_tablet_bookings.png"))
            tablet_bookings_grid = page.locator("#bookings-table-container .desktop-table-view").first
            tablet_bookings_cards = page.locator("#bookings-table-container .mobile-record-list").first
            if tablet_bookings_grid.count() == 0 or not tablet_bookings_grid.is_visible():
                raise SystemExit("Responsive smoke failed: tablet grid view is not visible.")
            if tablet_bookings_cards.count() > 0 and tablet_bookings_cards.is_visible():
                raise SystemExit("Responsive smoke failed: tablet should not show phone card list.")

        if name == "desktop":
            safe_click(page, "#nav-bookings")
            page.wait_for_timeout(1000)
            desktop_bookings_grid = page.locator("#bookings-table-container .desktop-table-view").first
            if desktop_bookings_grid.count() == 0 or not desktop_bookings_grid.is_visible():
                raise SystemExit("Responsive smoke failed: desktop grid view is not visible.")

        context.close()

def run_custody_smoke(page, logs_dir):
    print("[CUSTODY_SMOKE] step 1: open custody tab")
    open_tab(page, "#nav-dress-custody", "#view-dress-custody", "#dc-search")
    page.wait_for_timeout(1000)

    print("[CUSTODY_SMOKE] step 2: select first existing custody record")
    wait_dropdown_ready(page, "dc-search", timeout_ms=20000)

    def _first_dropdown_option():
        for sel in [
            ".dash-dropdown-option:visible",
            ".Select-option:visible",
            ".VirtualizedSelectOption:visible",
            "[role='option']:visible",
        ]:
            try:
                candidate = page.locator(sel).first
                if candidate.count() > 0:
                    return candidate
            except Exception:
                pass
        return None

    page.locator("#dc-search").click(force=True)
    page.wait_for_timeout(300)
    option = _first_dropdown_option()
    if option is None:
        print("[CUSTODY_SMOKE] no existing custody record, creating one for smoke")
        safe_click(page, "#btn-open-custody-modal")
        page.wait_for_selector("#modal-custody-workflow .modal-content", state="visible", timeout=10000)
        wait_dropdown_ready(page, "dc-booking", timeout_ms=20000)
        page.locator("#dc-booking").click(force=True)
        page.wait_for_timeout(300)
        preferred_booking = None
        for sel in [
            ".dash-dropdown-option:visible",
            ".Select-option:visible",
            ".VirtualizedSelectOption:visible",
            "[role='option']:visible",
        ]:
            try:
                preferred_booking = page.locator(sel, has_text="بدون فستان").first
                if preferred_booking.count() > 0:
                    break
            except Exception:
                preferred_booking = None
        if preferred_booking and preferred_booking.count() > 0:
            preferred_booking.click(force=True)
        else:
            select_first_option(page, "dc-booking")
        page.fill("#dc-deposit-amount", "500")
        page.fill("#dc-guarantee-type", "بطاقة")
        page.fill("#dc-guarantee-reference", "SMOKE-REF")
        page.fill("#dc-create-notes", "Smoke custody record")
        safe_click(page, "#btn-save-custody-workflow")
        page.wait_for_timeout(1800)
        page.locator("#dc-search").click(force=True)
        page.wait_for_timeout(300)
        option = _first_dropdown_option()
    if option is None:
        page.screenshot(path=str(logs_dir / "e2e_custody_no_options.png"))
        raise SystemExit("CUSTODY_SMOKE failed: no custody records are available after create attempt.")

    option_text = option.inner_text().strip()
    option.click(force=True)
    page.wait_for_timeout(1200)

    summary_text = page.locator("#dc-summary").inner_text().strip()
    if NEXT_ACTION_LABEL not in summary_text:
        print("[CUSTODY_SMOKE] summary did not refresh from dropdown selection, continuing with row action check")

    print("[CUSTODY_SMOKE] step 3: open next action from row")
    action_cell = page.locator("#dress-custody-table-container .ag-cell.ag-action-cell", has_text=NEXT_ACTION_LABEL).first
    if action_cell.count() == 0:
        page.screenshot(path=str(logs_dir / "e2e_custody_no_enabled_action.png"))
        raise SystemExit("CUSTODY_SMOKE failed: no next action cell was found.")
    action_cell.click(force=True)
    page.wait_for_selector(
        "#modal-custody-workflow .modal-content",
        state="visible",
        timeout=10000,
    )
    page.screenshot(path=str(logs_dir / "e2e_custody_modal_open.png"))
    safe_click(page, "#btn-close-custody-workflow")
    wait_for_no_modal(page, timeout_ms=3000)
    print(f"[CUSTODY_SMOKE] selected record: {option_text}")


def run_custody_compensation_smoke(page, logs_dir, ts, today):
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import logic
    from models import Booking, DressCustody, Payment, SessionLocal

    tag = f"E2E-COMP-{ts}"
    booking_no_extra = None
    booking_with_extra = None
    custody_no_extra = None
    custody_with_extra = None
    expected_payment_id = None

    def _assert_ok(result, action_name):
        if not isinstance(result, tuple) or not result or not result[0]:
            raise SystemExit(f"COMPENSATION_SMOKE failed at {action_name}: {result}")
        return result

    def _cleanup():
        session = SessionLocal()
        try:
            booking_ids = [bid for bid in [booking_no_extra, booking_with_extra] if bid]
            custody_ids = [cid for cid in [custody_no_extra, custody_with_extra] if cid]
            if booking_ids:
                session.query(Payment).filter(Payment.booking_id.in_(booking_ids)).delete(synchronize_session=False)
                session.query(DressCustody).filter(DressCustody.booking_id.in_(booking_ids)).delete(synchronize_session=False)
                session.query(Booking).filter(Booking.booking_id.in_(booking_ids)).delete(synchronize_session=False)
            if custody_ids:
                session.query(Payment).filter(Payment.source_custody_id.in_(custody_ids)).delete(synchronize_session=False)
                session.query(DressCustody).filter(DressCustody.custody_id.in_(custody_ids)).delete(synchronize_session=False)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    try:
        print("[COMPENSATION_SMOKE] step 1: create two custody scenarios")
        event_1 = (today + timedelta(days=430)).isoformat()
        event_2 = (today + timedelta(days=431)).isoformat()

        add_1 = _assert_ok(
            logic.add_booking(
                customer_name=f"{tag} NO-EXTRA",
                dept="عام",
                service=f"{tag} SERVICE",
                dress_code="-",
                event_date=event_1,
                price=1000,
                paid=0,
                status="نشط",
                notes=tag,
                reg_date=today.isoformat(),
            ),
            "add booking (deposit-only)",
        )
        booking_no_extra = add_1[2]

        add_2 = _assert_ok(
            logic.add_booking(
                customer_name=f"{tag} EXTRA",
                dept="عام",
                service=f"{tag} SERVICE",
                dress_code="-",
                event_date=event_2,
                price=1000,
                paid=0,
                status="نشط",
                notes=tag,
                reg_date=today.isoformat(),
            ),
            "add booking (extra)",
        )
        booking_with_extra = add_2[2]

        create_1 = _assert_ok(
            logic.create_dress_custody(
                booking_no_extra,
                deposit_amount=500,
                guarantee_type="بطاقة",
                guarantee_reference=f"{tag}-A",
                notes=tag,
                handled_by="e2e",
                created_date=today.isoformat(),
            ),
            "create custody (deposit-only)",
        )
        custody_no_extra = create_1[2]

        create_2 = _assert_ok(
            logic.create_dress_custody(
                booking_with_extra,
                deposit_amount=500,
                guarantee_type="بطاقة",
                guarantee_reference=f"{tag}-B",
                notes=tag,
                handled_by="e2e",
                created_date=today.isoformat(),
            ),
            "create custody (extra)",
        )
        custody_with_extra = create_2[2]

        _assert_ok(
            logic.handover_dress_custody(custody_no_extra, handover_date=today.isoformat(), notes=tag, handled_by="e2e"),
            "handover custody (deposit-only)",
        )
        _assert_ok(
            logic.handover_dress_custody(custody_with_extra, handover_date=today.isoformat(), notes=tag, handled_by="e2e"),
            "handover custody (extra)",
        )

        _assert_ok(
            logic.receive_dress_from_customer(
                custody_no_extra,
                return_date=today.isoformat(),
                condition_in="good",
                damage_notes=f"{tag} deposit-only",
                handled_by="e2e",
                has_damage=True,
                compensation_amount=300,
                guarantee_returned=True,
                guarantee_return_date=today.isoformat(),
            ),
            "receive custody (deposit-only)",
        )
        _assert_ok(
            logic.receive_dress_from_customer(
                custody_with_extra,
                return_date=today.isoformat(),
                condition_in="damage",
                damage_notes=f"{tag} extra",
                handled_by="e2e",
                has_damage=True,
                compensation_amount=900,
                guarantee_returned=True,
                guarantee_return_date=today.isoformat(),
            ),
            "receive custody (extra)",
        )

        print("[COMPENSATION_SMOKE] step 2: verify accounting invariants in DB")
        session = SessionLocal()
        try:
            no_extra_payments = (
                session.query(Payment)
                .filter_by(source_custody_id=custody_no_extra, payment_kind="custody_compensation")
                .all()
            )
            if no_extra_payments:
                raise SystemExit(
                    "COMPENSATION_SMOKE failed: deposit-only case created compensation voucher unexpectedly."
                )

            extra_payments = (
                session.query(Payment)
                .filter_by(source_custody_id=custody_with_extra, payment_kind="custody_compensation")
                .all()
            )
            if len(extra_payments) != 1:
                raise SystemExit(
                    f"COMPENSATION_SMOKE failed: expected 1 compensation voucher, found {len(extra_payments)}."
                )

            voucher = extra_payments[0]
            expected_payment_id = str(voucher.payment_id or "").strip()
            amount = float(voucher.amount or 0)
            remaining = float(voucher.remaining_after or 0)
            if abs(amount - 400.0) > 0.01:
                raise SystemExit(
                    f"COMPENSATION_SMOKE failed: voucher amount expected 400.00 but got {amount:.2f}."
                )
            if abs(remaining) > 0.01:
                raise SystemExit(
                    f"COMPENSATION_SMOKE failed: voucher remaining_after expected 0.00 but got {remaining:.2f}."
                )
            if "سند تعويض" not in str(voucher.display_label or ""):
                raise SystemExit(
                    "COMPENSATION_SMOKE failed: display label does not include 'سند تعويض'."
                )
            if not expected_payment_id:
                raise SystemExit(
                    "COMPENSATION_SMOKE failed: compensation voucher id is empty."
                )
        finally:
            session.close()

        print("[COMPENSATION_SMOKE] step 3: verify voucher visibility in payments module")
        payments_text = ""
        found_label = False
        found_payment_id = False
        # App-side cached data can delay visibility for up to cache TTL.
        for _ in range(8):
            open_tab(page, "#nav-payments", "#view-payments", "#payments-table-container")
            try:
                if page.locator("#p-search").count() > 0:
                    select_by_text(page, "p-search", expected_payment_id)
                    page.wait_for_timeout(800)
            except Exception:
                pass
            page.wait_for_timeout(1400)
            payments_text = page.locator("#payments-table-container").inner_text()
            found_label = "سند تعويض" in payments_text
            found_payment_id = expected_payment_id in payments_text
            if found_label and found_payment_id:
                break
            page.wait_for_timeout(10000)

        if not found_payment_id:
            page.screenshot(path=str(logs_dir / "e2e_compensation_missing_payment_id.png"))
            raise SystemExit(
                "COMPENSATION_SMOKE failed: expected compensation voucher id not visible in payments module."
            )
        if not found_label:
            print(
                "[COMPENSATION_SMOKE] info: payment voucher found in payments module, "
                "but label text was not visible in rendered table viewport."
            )
        page.screenshot(path=str(logs_dir / "e2e_compensation_payments.png"))
        print("[COMPENSATION_SMOKE] completed successfully")

    finally:
        _cleanup()
