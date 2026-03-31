def rows(records):
    return records if isinstance(records, list) else []


def text(value):
    return str(value or "").strip()


def float_value(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def map_lookup(record_map, record_id):
    if not isinstance(record_map, dict):
        return None
    candidates = [record_id, text(record_id)]
    for candidate in candidates:
        if candidate in record_map:
            return record_map[candidate]
        if candidate is not None and str(candidate) in record_map:
            return record_map[str(candidate)]
    return None


def same_value(left, right):
    return text(left) == text(right)
