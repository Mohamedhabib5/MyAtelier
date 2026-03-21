from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def norm_text(val):
    if val is None:
        return ""
    return str(val).replace("\u00A0", " ").strip()


def norm_code(val):
    return "".join(norm_text(val).split())


# Backward-compatible private alias for existing internal usage.
_norm_text = norm_text


def format_date_ddmmyyyy(value):
    """
    Normalize date-like inputs to DD/MM/YYYY for UI display.
    Returns empty string when value is missing/invalid.
    """
    text_value = norm_text(value)
    if not text_value:
        return ""

    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            parsed = datetime.strptime(text_value, fmt)
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            continue
    return ""


_MONEY_QUANT = Decimal("0.01")


def money(value):
    try:
        raw = str(value).strip() if value is not None else "0"
        if raw == "":
            raw = "0"
        dec = Decimal(raw)
    except (InvalidOperation, ValueError, TypeError):
        dec = Decimal("0")
    return dec.quantize(_MONEY_QUANT, rounding=ROUND_HALF_UP)


def money_float(value):
    return float(money(value))
