# AGENTS.md

## Project Scope
- Active app entrypoint: `app_dash.py`
- Primary modules: `logic.py`, `models.py`, `assets/custom.css`
- Test scripts: `scripts/health_check.py`, `scripts/e2e_playwright.py`

## Source Of Truth
- Edit only root working files unless explicitly asked otherwise.
- Do not modify files under `backups/` or `releases/` unless user requests it.
- Keep all old backups and release snapshots.

## Change Policy (Small Steps Only)
- One small objective per request.
- Change at most `1-2` files per step when possible.
- Keep diffs small (target `<= 120` lines changed per step).
- Do not perform broad refactors unless explicitly requested.
- Do not rename many symbols/files in one step.

## Safety Rules
- Never use destructive commands (`git reset --hard`, mass delete, etc.).
- Do not remove backup folders or release archives.
- Keep behavior unchanged unless change is explicitly requested.
- Preserve existing Arabic labels/messages unless requested to change them.

## Required Validation After Each Change
1. Syntax check:
   - `python -m py_compile app_dash.py logic.py models.py`
2. App run check:
   - run `python app_dash.py`
   - verify app opens on `http://127.0.0.1:8050`
3. Data health check:
   - `python scripts/health_check.py`
4. If UI/flows changed:
   - run targeted browser checks (or `python scripts/e2e_playwright.py` when needed)

## Response Format For Every Agent Change
- Files changed
- What changed
- What was tested
- Result (PASS/FAIL)
- Known risks (if any)

## Backup Workflow
- Before high-risk changes (DB schema/data migration/core booking/payment logic), create a timestamped backup folder under `backups/`.
- Keep baseline snapshots intact.
