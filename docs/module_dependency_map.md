# MyAtelier Module Dependency Map
Updated: Tuesday, February 17, 2026

## Layered Architecture
1. `app_dash.py` (Entrypoint)
2. `app/composition/*` (Runtime wiring/factories)
3. `app/layouts/*` + `app/table_content/*` + `app/ui/*` (UI building blocks)
4. `app/callbacks/*` (behavior/callback registration)
5. `logic.py` / `models.py` (data/business layer)

## Entrypoint Responsibility (`app_dash.py`)
- Create Dash app/server via `app/bootstrap.py`.
- Define flask route for dress images.
- Build runtime wiring via `app/composition/wiring.py`.
- Assign root layout via `app/layouts/root.py`.
- Register callbacks via `app/callbacks/register_all.py`.
- Start app process (`app.run`).

## Composition Responsibility
- `app/composition/wiring.py`:
  - Creates `create_dt` wrapper.
  - Builds table-content callables from `app/table_content/factory.py`.
  - Builds `main_layout` callable via `app/composition/layout_factory.py`.
- `app/composition/layout_factory.py`:
  - Adapts dependencies into `layout_main(...)`.

## UI/Feature Modules
- `app/layouts/*`: pure layout functions for feature views.
- `app/table_content/*`: table sections per feature.
- `app/ui/grid.py`: shared AG Grid rendering helper.

## Callback Modules
- `app/callbacks/register_all.py`: single callback registration entrypoint.
- Feature callback files under `app/callbacks/` contain feature-specific behavior.

## Dependency Rules (Must Keep)
1. `app_dash.py` may import from `composition`, `layouts`, `callbacks`, `constants`, `text_utils`, `logic`.
2. `composition` may import from `layouts`, `table_content`, `ui`; avoid importing from `callbacks`.
3. `layouts` should not import `callbacks`.
4. `callbacks` can consume wiring dependencies passed from `app_dash.py`; avoid hard-coding cross-feature imports when possible.
5. Shared constants/helpers belong in `app/constants.py` and `app/text_utils.py`.

## Anti-Conflict Edit Guide
1. UI structure change: edit only `app/layouts/<feature>.py`.
2. Table content change: edit only `app/table_content/<feature>.py`.
3. Callback behavior change: edit only `app/callbacks/<feature>_*.py`.
4. Cross-feature wiring change: edit `app/composition/wiring.py`.
5. App startup/runtime change: edit `app_dash.py` and/or `app/bootstrap.py`.

## Final QA Gate
1. `python -m py_compile app_dash.py logic.py models.py`
2. `python -c "import app_dash; print('callbacks', len(app_dash.app.callback_map))"`
3. `python scripts/health_check.py`
4. `python app_dash.py` and verify `http://127.0.0.1:8050`
5. If UI flows changed, run `python scripts/e2e_playwright.py`
