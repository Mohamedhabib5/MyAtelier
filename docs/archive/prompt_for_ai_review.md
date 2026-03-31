# Prompt for AI Review of MyAtelier Technical Report

> STATUS: Historical/internal tooling prompt.
> This file is a helper prompt for external review workflows and is not a source of truth for the current app state.

Copy everything below this line and paste it to any AI IDE:

---

You are reviewing a Python Dash project called **MyAtelier** (a bridal atelier management system).

## Your Task

1. Read the file `docs/technical_report_and_execution_plan.md` in this project.
2. Cross-reference the report against the actual codebase — specifically these files:
   - `app_dash.py` (entrypoint)
   - `logic.py` (business logic — 1142 lines)
   - `models.py` (ORM models)
   - `app/callbacks/register_all.py` (callback hub)
   - `app/callbacks/auth.py` (authentication)
   - `app/callbacks/bookings_form.py` (largest callback)
   - `app/composition/wiring.py` (dependency injection)
   - `app/services/backup_service.py` (backup system)
   - `app/table_content/dresses.py` (67KB — investigate why it's so large)
   - `scripts/health_check.py` (data integrity checks)
   - `scripts/e2e_playwright.py` (E2E tests — 1489 lines)
   - `.gitignore`
3. Then produce the following assessment:

## What To Produce

### A) Report Accuracy Check
- Are the claims in the report accurate when compared to the actual code?
- Are there any risks or issues the report missed?
- Are there any risks the report overstated?
- Is the file size / line count data accurate?

### B) Execution Plan Assessment
- Do you agree with the proposed phase ordering? If not, what would you change and why?
- Are there any missing steps or gaps in the plan?
- Are the exit criteria realistic and verifiable?
- Are there any dependencies between phases that the plan doesn't account for?

### C) Your Own Recommendations
- What would YOU prioritize differently and why?
- Do you see any quick wins the report missed?
- Are there architectural improvements not covered in the plan?
- What's your assessment of the E2E phase1b2 hang — do you have a different theory on the root cause?

### D) Risk Assessment
- Do you agree with the severity rankings in the risk registry?
- Would you add or remove any risks?
- What's the single most important thing to fix first?

## Rules
- Do NOT modify any code or run any commands.
- Be specific — cite file names, line numbers, and function names.
- If you disagree with the report, explain exactly why with evidence from the code.
- Be direct and opinionated, not generic.
