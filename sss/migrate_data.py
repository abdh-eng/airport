# migrate_data.py
# سكربت لترحيل البيانات من الملف القديم (data.json) إلى البنية الجديدة (data_store.json)

import json
import hashlib
from pathlib import Path

OLD_FILE = "data.json"        # اسم الملف القديم
NEW_FILE = "data_store.json"  # اسم الملف الجديد

def hash_password(pw) -> str:
    """إرجاع sha256 hash لكلمة المرور النصية أو أي نوع آخر"""
    if not isinstance(pw, str):
        pw = str(pw)  # نحول أي dict/list/... إلى نص
    return hashlib.sha256(pw.encode()).hexdigest()

def migrate():
    if not Path(OLD_FILE).exists():
        print(f"❌ الملف {OLD_FILE} غير موجود!")
        return

    with open(OLD_FILE, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    new_data = {"users": [], "cars": [], "invoices": []}

    # ---- ترحيل المستخدمين ----
    for u in old_data.get("users", []):
        if isinstance(u, dict):
            new_data["users"].append({
                "id": u.get("id", f"user-{u.get('username','xxx')}"),
                "username": u.get("username", ""),
                "password_hash": hash_password(u.get("password", "123456")),
                "usertype": u.get("usertype", "Customer"),
                "phone": u.get("phone", ""),
                "gender": u.get("gender", "M"),
                "is_active": u.get("is_active", True),
                "loyalty_points": u.get("loyalty_points", 0)
            })
        elif isinstance(u, list):
            username = u[0] if len(u) > 0 else "unknown"
            password = u[1] if len(u) > 1 else "123456"
            usertype = u[2] if len(u) > 2 else "Customer"
            phone    = u[3] if len(u) > 3 else ""
            gender   = u[4] if len(u) > 4 else "M"

            new_data["users"].append({
                "id": f"user-{username}",
                "username": username,
                "password_hash": hash_password(password),
                "usertype": usertype,
                "phone": phone,
                "gender": gender,
                "is_active": True,
                "loyalty_points": 0
            })

    # ---- ترحيل السيارات ----
    for c in old_data.get("cars", []):
        specs_parts = []
        for key in c:
            if key not in ("id","name","model","price","color","status","specs"):
                specs_parts.append(f"{key}:{c[key]}")
        specs_str = ", ".join(specs_parts + [c.get("specs","")])
        new_data["cars"].append({
            "id": c.get("id", f"car-{c.get('name','xxx')}"),
            "name": c.get("name", ""),
            "model_year": c.get("model", 0),
            "price": c.get("price", 0.0),
            "color": c.get("color", ""),
            "specs": specs_str.strip(),
            "status": c.get("status", "available")
        })

    # ---- ترحيل الفواتير ----
    for i in old_data.get("invoices", []):
        new_data["invoices"].append({
            "id": i.get("id", f"inv-{i.get('customer','xxx')}"),
            "customer": i.get("customer", ""),
            "car_id": i.get("car_id", ""),
            "price": i.get("price", 0.0),
            "points_earned": i.get("points_earned", 0),
            "date": i.get("date", "")
        })

    # ---- حفظ الملف الجديد ----
    with open(NEW_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print(f"✅ تم الترحيل بنجاح! البيانات الجديدة محفوظة في {NEW_FILE}")

if __name__ == "__main__":
    migrate()
