# Manual Test Checklist

## Scope
- Project: `MyAtelier`
- App entry: `app_dash.py`
- Baseline backup: `backups/baseline_20260215_223257`
- Baseline release zip: `releases/baseline_20260215_223257.zip`

## Run
1. Start app: `python app_dash.py`
2. Open: `http://127.0.0.1:8050`
3. Login with valid user.

## Quick Smoke (Run After Every Small Change)
1. Home/Finance tab opens without errors.
2. Customers tab opens and customers table is visible.
3. Bookings tab opens and bookings table is visible.
4. Payments tab opens and payments table is visible.
5. Settings tab opens and departments table is visible.

## Data Actions (Minimum)
1. Add customer, then edit same customer, then delete if no linked bookings.
2. Add service, then edit same service, then delete if no linked bookings.
3. Add dress, then edit same dress, then delete if no linked bookings.
4. Add booking with valid data.
5. Add payment for an existing booking.

## Safety Checks
1. Trying to delete linked customer shows block message.
2. Trying to delete linked service shows block message.
3. Trying to delete linked booking with payments shows block message.
4. Export button downloads CSV from each main table.

## Notes Template
- Date:
- Change tested:
- Tabs checked:
- CRUD checked:
- Any error message:
- Result: PASS / FAIL

