# Message Feedback Policy

## Scope
- Applies to all user-facing operation feedback (CRUD, auth, details, settings).

## Standard Behavior
- Success:
  - Use global `app-success-toast`.
  - Auto-dismiss after `3000ms`.
  - Message should be short and action-specific.
- Warning / Error:
  - Use `dbc.Alert` near the relevant form/section.
  - Keep visible until user closes it or next valid action clears it.
  - Prefer `dismissable=True` where practical.

## Consistency Rules
- Do not show silent outcomes for write actions.
- Do not mix success `Alert` and success `Toast` for the same flow.
- Keep Arabic text clear and UTF-8 clean (no mojibake).

## Mapping Guide
- Validation input issues -> `warning Alert`
- Business rule/constraint failure -> `danger Alert`
- Successful add/edit/delete -> `success Toast`

## Rollout Order
1. bookings (reference implementation already includes success toast)
2. payments
3. services
4. dresses
5. customers
6. settings/users
