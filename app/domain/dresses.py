import base64
import os
from datetime import date

from models import Booking, Dress, SessionLocal


def _norm_text(val):
    if val is None:
        return ""
    return str(val).replace("\u00A0", " ").strip()


def _norm_code(val):
    return "".join(_norm_text(val).split())


def save_image(image_contents, dress_code, *, image_folder):
    if not image_contents:
        return True, ""
    try:
        max_size = 300 * 1024
        header, content_string = image_contents.split(",")
        decoded = base64.b64decode(content_string)
        if len(decoded) > max_size:
            return False, "\u062d\u062c\u0645 \u0627\u0644\u0635\u0648\u0631\u0629 \u0643\u0628\u064a\u0631"

        ext = ".jpg"
        if "png" in header:
            ext = ".png"
        elif "webp" in header:
            ext = ".webp"

        filename = f"{dress_code}{ext}"
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        with open(os.path.join(image_folder, filename), "wb") as f:
            f.write(decoded)
        return True, filename
    except Exception as e:
        return False, str(e)


def add_dress(
    code,
    d_type,
    date_buy,
    status,
    desc,
    image_contents=None,
    *,
    image_folder,
    msg_missing_info="",
    msg_code_exists="",
    msg_added="",
):
    if not code or not desc:
        return False, msg_missing_info

    session = SessionLocal()
    try:
        if session.query(Dress).filter_by(dress_code=code).first():
            return False, msg_code_exists

        img_path = ""
        if image_contents:
            succ, res = save_image(image_contents, code, image_folder=image_folder)
            if succ:
                img_path = res
            else:
                return False, res

        d = Dress(
            dress_code=code,
            d_type=d_type,
            buy_date=str(date_buy),
            description=desc,
            status=status,
            image_path=img_path,
        )
        session.add(d)
        session.commit()
        return True, msg_added
    finally:
        session.close()


def update_dress(
    old_code,
    new_code,
    d_type,
    date_buy,
    status,
    desc,
    image_contents=None,
    *,
    image_folder,
    msg_not_found="",
    msg_new_code_exists="",
    msg_updated="",
):
    session = SessionLocal()
    try:
        d = session.query(Dress).filter_by(dress_code=old_code).first()
        if not d:
            return False, msg_not_found

        if old_code != new_code and session.query(Dress).filter_by(dress_code=new_code).first():
            return False, msg_new_code_exists

        if old_code != new_code:
            if d.image_path:
                try:
                    ext = os.path.splitext(d.image_path)[1]
                    new_img = f"{new_code}{ext}"
                    os.rename(os.path.join(image_folder, d.image_path), os.path.join(image_folder, new_img))
                    d.image_path = new_img
                except Exception:
                    pass
            old_norm = _norm_code(old_code)
            new_norm = _norm_code(new_code)
            if old_norm and old_norm != new_norm:
                for b in session.query(Booking).all():
                    if _norm_code(b.dress_code) == old_norm:
                        b.dress_code = new_code

        if image_contents:
            succ, res = save_image(image_contents, new_code, image_folder=image_folder)
            if succ:
                d.image_path = res
            else:
                return False, res

        d.dress_code = new_code
        d.d_type = d_type
        d.buy_date = str(date_buy)
        d.status = status
        d.description = desc
        session.commit()
        return True, msg_updated
    finally:
        session.close()


def delete_dress(d_code, *, image_folder, msg_not_found="", msg_has_bookings="", msg_deleted=""):
    session = SessionLocal()
    try:
        d = session.query(Dress).filter_by(dress_code=d_code).first()
        if not d:
            return False, msg_not_found
        target_code = _norm_code(d_code)
        has_booking = False
        for row in session.query(Booking.dress_code).all():
            if _norm_code(row[0]) == target_code and target_code:
                has_booking = True
                break
        if has_booking:
            return False, msg_has_bookings

        if d.image_path:
            img_path = os.path.join(image_folder, d.image_path)
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except OSError:
                    pass
        session.delete(d)
        session.commit()
        return True, msg_deleted
    finally:
        session.close()

