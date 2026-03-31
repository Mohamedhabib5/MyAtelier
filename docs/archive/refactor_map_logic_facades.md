# Logic Facade Refactor Map

Date: 2026-03-05

> STATUS: Historical refactor snapshot.
> This file records a refactor state at a point in time and should not override the current architecture docs.

## Purpose
Track which `logic.py` wrappers now delegate to dedicated facade modules under `app/domain/`.

## Moved Wrapper Blocks

### Departments
- Source facade: `app/domain/departments_facade.py`
- `check_departments`
- `add_department`
- `update_department`
- `delete_department`
- `save_department`

### Customers
- Source facade: `app/domain/customers_facade.py`
- `add_customer`
- `update_customer`
- `delete_customer`

### Services
- Source facade: `app/domain/services_facade.py`
- `add_service`
- `update_service`
- `delete_service`

### Dresses
- Source facade: `app/domain/dresses_facade.py`
- `save_image`
- `add_dress`
- `update_dress`
- `delete_dress`

### Bookings
- Source facade: `app/domain/bookings_facade.py`
- `add_booking`
- `update_booking`
- `delete_booking`

### Payments
- Source facade: `app/domain/payments_facade.py`
- `add_payment`
- `update_payment`
- `delete_payment`

## Notes
- `logic.py` remains the compatibility layer and public entrypoint.
- Function signatures exposed by `logic.py` were preserved.
- Validation after each step: compile, health check, pytest, app probe.
