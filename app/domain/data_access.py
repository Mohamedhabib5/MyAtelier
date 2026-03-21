import pandas as pd
import time

from models import Booking, Customer, Dress, Payment, Service, SessionLocal


# Column mappings (DB English -> App Arabic).
C_COLS_MAP = {
    "customer_id": "\u0643\u0648\u062f \u0627\u0644\u0639\u0645\u064a\u0644",
    "reg_date": "\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u062a\u0633\u062c\u064a\u0644",
    "name": "\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u0648\u0633\u0647",
    "groom_name": "\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u064a\u0633",
    "address": "\u0627\u0644\u0639\u0646\u0648\u0627\u0646",
    "phone1": "\u062a\u0644\u064a\u0641\u0648\u0646 1",
    "phone2": "\u062a\u0644\u064a\u0641\u0648\u0646 2",
    "notes": "\u0645\u0644\u0627\u062d\u0638\u0627\u062a",
}

S_COLS_MAP = {
    "service_id": "\u0643\u0648\u062f \u0627\u0644\u062e\u062f\u0645\u0629",
    "department": "\u0627\u0644\u0642\u0633\u0645",
    "name": "\u0627\u0633\u0645 \u0627\u0644\u062e\u062f\u0645\u0629",
    "price": "\u0627\u0644\u0633\u0639\u0631 \u0627\u0644\u0645\u0642\u062a\u0631\u062d",
}

D_COLS_MAP = {
    "dress_code": "\u0643\u0648\u062f \u0627\u0644\u0641\u0633\u062a\u0627\u0646",
    "d_type": "\u0646\u0648\u0639 \u0627\u0644\u0641\u0633\u062a\u0627\u0646",
    "buy_date": "\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u0634\u0631\u0627\u0621",
    "description": "\u0648\u0635\u0641 \u0627\u0644\u0641\u0633\u062a\u0627\u0646",
    "image_path": "\u0635\u0648\u0631\u0629 \u0627\u0644\u0641\u0633\u062a\u0627\u0646",
    "status": "\u062d\u0627\u0644\u0629 \u0627\u0644\u0641\u0633\u062a\u0627\u0646",
}

B_COLS_MAP = {
    "booking_id": "\u0643\u0648\u062f \u0627\u0644\u062d\u062c\u0632",
    "booking_date": "\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u062d\u062c\u0632",
    "customer_name": "\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u0648\u0633\u0647",
    "department": "\u0627\u0644\u0642\u0633\u0645",
    "service": "\u0627\u0644\u062e\u062f\u0645\u0629",
    "dress_code": "\u0643\u0648\u062f \u0627\u0644\u0641\u0633\u062a\u0627\u0646",
    "event_date": "\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u0645\u0646\u0627\u0633\u0628\u0629",
    "price": "\u0627\u0644\u0633\u0639\u0631 \u0627\u0644\u0645\u062a\u0641\u0642",
    "paid": "\u0627\u0644\u0645\u062f\u0641\u0648\u0639",
    "remaining": "\u0627\u0644\u0645\u062a\u0628\u0642\u064a",
    "notes": "\u0645\u0644\u0627\u062d\u0638\u0627\u062a \u0627\u0644\u062d\u062c\u0632",
    "status": "\u062d\u0627\u0644\u0629 \u0627\u0644\u062d\u062c\u0632",
}

P_COLS_MAP = {
    "payment_id": "\u0643\u0648\u062f \u0627\u0644\u062f\u0641\u0639",
    "payment_date": "\u0627\u0644\u062a\u0627\u0631\u064a\u062e",
    "booking_id": "\u0643\u0648\u062f \u0627\u0644\u062d\u062c\u0632",
    "amount": "\u0627\u0644\u0642\u064a\u0645\u0629 \u0627\u0644\u0645\u062f\u0641\u0648\u0639\u0629",
    "customer_name": "\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u0648\u0633\u0647",
    "groom_name": "\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u064a\u0633",
    "remaining_after": "\u0627\u0644\u0645\u062a\u0628\u0642\u064a \u0628\u0639\u062f \u0627\u0644\u062f\u0641\u0639\u0629",
    "notes": "\u0645\u0644\u0627\u062d\u0638\u0627\u062a \u0627\u0644\u062f\u0641\u0639",
}

C_COLS = list(C_COLS_MAP.values())
S_COLS = list(S_COLS_MAP.values())
D_COLS = list(D_COLS_MAP.values())
B_COLS = list(B_COLS_MAP.values())
P_COLS = list(P_COLS_MAP.values())

CACHE_TTL_SECONDS = 2.0
DATA_CACHE = {}
CACHE_STATS = {"hits": 0, "misses": 0}


def invalidate_data_cache(file_name=None):
    if file_name:
        DATA_CACHE.pop(str(file_name), None)
        return
    DATA_CACHE.clear()


def get_cache_stats():
    return dict(CACHE_STATS)


def reset_cache_stats():
    CACHE_STATS["hits"] = 0
    CACHE_STATS["misses"] = 0


def invalidate_after_write(result, file_name=None, *, invalidate_fn=invalidate_data_cache):
    ok = False
    if isinstance(result, bool):
        ok = result
    elif isinstance(result, tuple) and result:
        ok = bool(result[0])
    if ok:
        invalidate_fn(file_name=file_name)
    return result


def invalidate_many(file_names, *, invalidate_fn=invalidate_data_cache):
    for fname in file_names:
        invalidate_fn(file_name=fname)


def load_data(file_name, columns=None):
    cache_key = str(file_name)
    now = time.time()
    cached = DATA_CACHE.get(cache_key)
    if cached:
        ts, df_cached = cached
        if (now - ts) <= CACHE_TTL_SECONDS:
            CACHE_STATS["hits"] += 1
            df = df_cached.copy()
            if columns:
                for c in columns:
                    if c not in df.columns:
                        df[c] = ""
                return df[columns]
            return df
    CACHE_STATS["misses"] += 1

    session = SessionLocal()
    try:
        if "customers" in file_name:
            q = session.query(Customer).all()
            data = [{v: getattr(i, k) for k, v in C_COLS_MAP.items()} for i in q]
            df = pd.DataFrame(data, columns=C_COLS_MAP.values()).fillna("")
        elif "services" in file_name:
            q = session.query(Service).all()
            data = [{v: getattr(i, k) for k, v in S_COLS_MAP.items()} for i in q]
            df = pd.DataFrame(data, columns=S_COLS_MAP.values()).fillna("")
        elif "dresses" in file_name:
            q = session.query(Dress).all()
            data = [{v: getattr(i, k) for k, v in D_COLS_MAP.items()} for i in q]
            df = pd.DataFrame(data, columns=D_COLS_MAP.values()).fillna("")
        elif "bookings" in file_name:
            q = session.query(Booking).all()
            data = [{v: getattr(i, k) for k, v in B_COLS_MAP.items()} for i in q]
            df = pd.DataFrame(data, columns=B_COLS_MAP.values()).fillna("")
        elif "payments" in file_name:
            q = session.query(Payment).all()
            data = [{v: getattr(i, k) for k, v in P_COLS_MAP.items()} for i in q]
            df = pd.DataFrame(data, columns=P_COLS_MAP.values()).fillna("")
        else:
            return pd.DataFrame()

        if columns:
            for c in columns:
                if c not in df.columns:
                    df[c] = ""
            df = df[columns]
        DATA_CACHE[cache_key] = (now, df.copy())
        return df
    except Exception as e:
        print(f"DB Load Error: {e}")
        return pd.DataFrame()
    finally:
        session.close()
