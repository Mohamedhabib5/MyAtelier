import re

from app.constants import DELETE_REASON_AR


def normalize_code(val):
    if val is None:
        return ""
    s = str(val)
    s = s.replace("\u00A0", " ").strip()
    s = re.sub(r"\s+", "", s)
    # Keep ASCII letters/numbers/dash for code comparisons
    s = re.sub(r"[^A-Za-z0-9-]", "", s)
    return s


def delete_reason(msg):
    return DELETE_REASON_AR.get(msg, msg)
