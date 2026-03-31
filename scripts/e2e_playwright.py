from pathlib import Path

from e2e_playwright_context import (
    BASE_URL,
    BOOKING_ONLY,
    CORE_SMOKE,
    COMPENSATION_SMOKE,
    CUSTODY_SMOKE,
    FULL_REGRESSION,
    HEADLESS,
    PASSWORD,
    RESPONSIVE_SMOKE,
    USERNAME,
    date,
    sync_playwright,
    time,
    timedelta,
)
from e2e_playwright_booking_flows import run_booking_only, run_core_smoke, run_full_phase1b1
from e2e_playwright_responsive_custody import run_custody_compensation_smoke, run_custody_smoke, run_responsive_smoke


def _mode_name():
    if RESPONSIVE_SMOKE:
        return "RESPONSIVE_SMOKE"
    if COMPENSATION_SMOKE:
        return "COMPENSATION_SMOKE"
    if BOOKING_ONLY:
        return "BOOKING_ONLY"
    if CORE_SMOKE:
        return "CORE_SMOKE"
    if CUSTODY_SMOKE:
        return "CUSTODY_SMOKE"
    if FULL_REGRESSION:
        return "FULL_REGRESSION"
    return "FULL_REGRESSION"


def main():
    ts = int(time.time())
    today = date.today()
    tomorrow = today + timedelta(days=1)
    same_day = (today + timedelta(days=365 + (ts % 100))).isoformat()

    bride_delete = f"E2E Bride Del {ts}"
    bride_booking = f"E2E Bride Book {ts}"
    bride_booking2 = f"E2E Bride Book2 {ts}"
    service_used = f"E2E Service Used {ts}"
    service_unused = f"E2E Service Unused {ts}"
    dress_used = f"DR{str(ts)[-6:]}"
    dress_unused = f"DU{str(ts)[-6:]}"

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    print(f"[E2E] mode={_mode_name()}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)

        if RESPONSIVE_SMOKE:
            run_responsive_smoke(browser, logs_dir)
            browser.close()
            print("RESPONSIVE_SMOKE completed successfully.")
            return

        page = browser.new_page(viewport={"width": 1400, "height": 1100})
        page.goto(BASE_URL, wait_until="networkidle")
        page.fill("#login-username", USERNAME)
        page.fill("#login-password", PASSWORD)
        page.click("#login-btn")

        if BOOKING_ONLY:
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
        elif CORE_SMOKE:
            run_core_smoke(page, logs_dir, ts, service_used, bride_booking)
        elif CUSTODY_SMOKE:
            run_custody_smoke(page, logs_dir)
        elif COMPENSATION_SMOKE:
            run_custody_compensation_smoke(page, logs_dir, ts, today)
        else:
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


if __name__ == "__main__":
    main()
