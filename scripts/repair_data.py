from __future__ import annotations

import os
import sys
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import logic
from logic import SessionLocal, Dress


def _collect_missing_dresses():
    b_df = logic.load_data("bookings.csv", logic.B_COLS)
    d_df = logic.load_data("dresses.csv", logic.D_COLS)

    norm_to_raw = {}
    for raw in b_df.get("كود الفستان", []):
        norm = logic._norm_code(raw)
        if not norm or norm == "-" or norm.lower() == "nan":
            continue
        if norm not in norm_to_raw:
            norm_to_raw[norm] = str(raw).strip()

    existing = {logic._norm_code(c) for c in d_df.get("كود الفستان", [])}
    missing_norms = sorted([n for n in norm_to_raw.keys() if n not in existing])
    return missing_norms, norm_to_raw


def add_missing_dresses():
    missing_norms, norm_to_raw = _collect_missing_dresses()
    if not missing_norms:
        print("No missing dress codes found.")
        return

    session = SessionLocal()
    try:
        for norm in missing_norms:
            raw_code = norm_to_raw.get(norm, norm)
            session.add(
                Dress(
                    dress_code=raw_code,
                    d_type="",
                    buy_date=str(date.today()),
                    description="تمت الإضافة تلقائياً لربط الحجوزات",
                    image_path="",
                    status="محجوز",
                )
            )
        session.commit()
        print(f"Added {len(missing_norms)} missing dress records:", ", ".join(missing_norms))
    finally:
        session.close()


if __name__ == "__main__":
    add_missing_dresses()
