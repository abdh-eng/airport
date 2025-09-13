# car_dealership_oop_full_commented.py
# مشروع شركة بيع سيارات - نسخة كاملة مع تعليقات عربية سطر-بسطر
# المتطلبات: تسجيل، تسجيل دخول، 3 صلاحيات، إدارة مستخدمين، إدارة سيارات،
# بيع سيارات، فواتير، نقاط ولاء، تقارير، ووجود >=12 كلاس.
# لا يعتمد على مكتبات خارجية - يستخدم مكتبات بايثون القياسية فقط.

# ---------------------------------------------------------------------
# استيراد المكتبات القياسية اللازمة
# ---------------------------------------------------------------------
import json                      # للتعامل مع ملفات JSON (البيانات)
import uuid                      # لتوليد معرفات فريدة (IDs)
import getpass                   # لقراءة كلمة المرور دون عرضها على الشاشة
import hashlib                   # لتجزئة كلمات المرور (hash)
from datetime import datetime    # للحصول على التاريخ/الوقت عند إنشاء الفواتير
from typing import List, Optional  # لأنواع البيانات الواضحة في التعريفات

# ---------------------------------------------------------------------
# إعدادات/ثوابت عامة قابلة للتعديل بسهولة
# ---------------------------------------------------------------------
DATA_FILE = "data_store.json"   # اسم ملف تخزين البيانات (يمكن تغييره)
PASSWORD_MIN_LEN = 8            # الحد الأدنى لطول كلمة المرور (قابل للتعديل)

# ---------------------------------------------------------------------
# فئة IDGenerator: لتوليد معرفات (IDs) قصيرة ومنظمة
# ---------------------------------------------------------------------
class IDGenerator:
    """
    فئة مساعدة لتوليد معرفات (IDs) بصيغة واضحة.
    نستخدم uuid.uuid4() ثم نأخذ أجزاء منه لتقليل الطول مع الحفاظ على التفرد.
    """
    @staticmethod
    def new(prefix: str) -> str:
        # نعيد سلسلة مكونة من بادئة + '-' + أول 8 أحرف من uuid
        # مثال: user-1a2b3c4d
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

# ---------------------------------------------------------------------
# فئة HashUtil: لتجزئة كلمات المرور (hash)
# ---------------------------------------------------------------------
class HashUtil:
    """
    فئة مساعدة لتجزئة كلمة المرور بطريقة بسيطة باستخدام SHA-256.
    الهدف: عدم حفظ كلمات المرور نصيًا داخل ملف البيانات.
    ملاحظة أمان: bcrypt أقوى لكن يحتاج مكتبة خارجية.
    """
    @staticmethod
    def hash_password(password: str) -> str:
        # نعيد قيمة الهش كسلسلة سداسية عشرية
        return hashlib.sha256(password.encode()).hexdigest()

# ---------------------------------------------------------------------
# فئة User: الكلاس الأساسي لكل المستخدمين (Base user class)
# ---------------------------------------------------------------------
class User:
    """
    الكلاس الأساسي User يحتوي على الحقول المشتركة لكل أنواع المستخدمين:
    id, username, password_hash, usertype, phone, gender, is_active, loyalty_points.
    يوفر إلى/من dict لتسهيل التخزين والتحميل من JSON.
    """
    def __init__(self, username: str, password: str, usertype: str = "Customer",
                 phone: str = "", gender: str = "M"):
        # إنشاء معرف فريد عند إنشاء المستخدم
        self.id = IDGenerator.new("user")
        # اسم المستخدم (نستخدمه لتسجيل الدخول والبحث)
        self.username = username
        # تخزين هاش كلمة المرور (وليس النص)
        self.password_hash = HashUtil.hash_password(password)
        # نوع المستخدم: "Admin" أو "SalesEmployee" أو "Customer"
        self.usertype = usertype
        # رقم الهاتف (اختياري)
        self.phone = phone
        # الجنس (M أو F) — يمكن تعديله حسب الحاجة
        self.gender = gender
        # حالة الحساب: True => نشط، False => معطل
        self.is_active = True
        # نقاط الولاء للعملاء (تزداد عند عمليات الشراء)
        self.loyalty_points = 0

    def to_dict(self) -> dict:
        """
        تحويل الكائن إلى dict لبساطة الحفظ في JSON.
        نضمن أن كل الحقول المهمة تمثل في dict.
        """
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "usertype": self.usertype,
            "phone": self.phone,
            "gender": self.gender,
            "is_active": self.is_active,
            "loyalty_points": self.loyalty_points
        }

    @staticmethod
    def from_dict(data: dict) -> 'User':
        """
        إنشاء كائن User من dict (مقروء من JSON).
        ملاحظة: نستخدم "dummy" لكلمة المرور لأن الهش يأتي من الملف.
        """
        # نستخرج الحقول الأساسية، ونضع قيمة مبدئية لكلمة المرور ثم نستبدل الهش
        u = User(data["username"], "dummy", data.get("usertype", "Customer"),
                 data.get("phone", ""), data.get("gender", "M"))
        # نستخدم معرف الملف إن وُجد
        u.id = data.get("id", u.id)
        # نحتفظ بقيمة الهش المحفوظة في الملف (إن وُجد)
        u.password_hash = data.get("password_hash", u.password_hash)
        # حالة النشاط
        u.is_active = data.get("is_active", True)
        # نقاط الولاء إن وُجدت
        u.loyalty_points = data.get("loyalty_points", 0)
        return u

# ---------------------------------------------------------------------
# فئات فرعية للمستخدمين: Admin, SalesEmployee, Customer
# (تُستخدم لتوضيح الـ OOP وتلبية شرط وجود أكثر من كلاس)
# ---------------------------------------------------------------------
class Admin(User):
    """
    كلاس Admin يورث من User.
    يمكن إضافة وظائف خاصة بالمدير هنا، لكن يكفي الوراثة حالياً.
    """
    def __init__(self, username: str, password: str, phone: str = "", gender: str = "M"):
        # استدعاء منشئ الأب مع تعيين usertype إلى "Admin"
        super().__init__(username, password, "Admin", phone, gender)

class SalesEmployee(User):
    """
    كلاس موظف المبيعات يورث من User.
    يمكن إضافة صلاحيات أو خصائص خاصة لموظف المبيعات.
    """
    def __init__(self, username: str, password: str, phone: str = "", gender: str = "M"):
        super().__init__(username, password, "SalesEmployee", phone, gender)

class Customer(User):
    """
    كلاس العميل (Customer) يورث من User.
    يبقى في الوراثة لتوضيح التصميم الكائني.
    """
    def __init__(self, username: str, password: str, phone: str = "", gender: str = "M"):
        super().__init__(username, password, "Customer", phone, gender)

# ---------------------------------------------------------------------
# فئة Car: نموذج السيارة
# ---------------------------------------------------------------------
class Car:
    """
    كلاس يمثل سيارة في المخزون.
    الحقول: id, name, model_year, price, color, specs, status.
    الحالة status يمكن أن تكون: "available", "sold", "reserved", ...
    """
    def __init__(self, name: str, model_year: int, price: float, color: str, specs: str = ""):
        # معرف فريد للسيارة
        self.id = IDGenerator.new("car")
        # اسم/نوع السيارة (مثل: Toyota Corolla)
        self.name = name
        # سنة الموديل (مثال: 2020)
        self.model_year = model_year
        # السعر (رقم عشري)
        self.price = price
        # لون السيارة
        self.color = color
        # مواصفات إضافية كنص
        self.specs = specs
        # الحالة الافتراضية: متاحة للبيع
        self.status = "available"

    def to_dict(self) -> dict:
        """تحويل السيارة إلى dict لحفظها في JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "model_year": self.model_year,
            "price": self.price,
            "color": self.color,
            "specs": self.specs,
            "status": self.status
        }

    @staticmethod
    def from_dict(data: dict) -> 'Car':
        """إنشاء كائن Car من dict (مقروء من JSON)"""
        c = Car(data["name"], data.get("model_year", 0), data.get("price", 0.0),
                data.get("color", ""), data.get("specs", ""))
        # إعادة المعرف إن وُجد في الملف
        c.id = data.get("id", c.id)
        # استرجاع الحالة (متاحة/مباعة)
        c.status = data.get("status", "available")
        return c

# ---------------------------------------------------------------------
# فئة Invoice: نموذج الفاتورة
# ---------------------------------------------------------------------
class Invoice:
    """
    كلاس الفاتورة (Invoice).
    يحتوي المعرف، اسم العميل، معرف السيارة، السعر، النقاط المكتسبة، والتاريخ.
    """
    def __init__(self, customer_username: str, car_id: str, price: float, points_earned: int):
        # معرف الفاتورة الفريد
        self.id = IDGenerator.new("inv")
        # اسم المستخدم أو اسم العميل الذي اشترى السيارة
        self.customer = customer_username
        # معرف السيارة المباعة
        self.car_id = car_id
        # السعر المدفوع
        self.price = price
        # نقاط الولاء المكتسبة من هذه العملية
        self.points_earned = points_earned
        # تاريخ الإنشاء بصيغة قابلة للقراءة
        self.date = datetime.now().isoformat(sep=' ', timespec='seconds')

    def to_dict(self) -> dict:
        """تحويل الفاتورة إلى dict لحفظها"""
        return {
            "id": self.id,
            "customer": self.customer,
            "car_id": self.car_id,
            "price": self.price,
            "points_earned": self.points_earned,
            "date": self.date
        }

    @staticmethod
    def from_dict(data: dict) -> 'Invoice':
        """إنشاء الفاتورة من dict المحفوظة"""
        inv = Invoice(data.get("customer", ""), data.get("car_id", ""), data.get("price", 0.0), data.get("points_earned", 0))
        inv.id = data.get("id", inv.id)
        inv.date = data.get("date", inv.date)
        return inv

# ---------------------------------------------------------------------
# فئة Validator: قواعد التحقق من صحة المدخلات
# ---------------------------------------------------------------------
class Validator:
    """
    فئة تحتوي أساليب ثابتة للتحقق من صحة البيانات:
    - username_ok: تحقق من اسم المستخدم
    - password_ok: تحقق من قوة كلمة المرور
    - phone_ok: تحقق من رقم الهاتف
    - positive_number: تحقق من أن القيمة رقم موجب
    الهدف: فصل قواعد التحقق عن منطق الأعمال (separation of concerns).
    """
    @staticmethod
    def username_ok(username: str) -> bool:
        # اسم المستخدم يجب أن يكون طول >=3، يبدأ بحرف، ويتكون من حروف وأرقام فقط
        return len(username) >= 3 and username[0].isalpha() and username.isalnum()

    @staticmethod
    def password_ok(password: str) -> bool:
        # كلمة المرور يجب أن تكون أطول من الحد الأدنى وتحتوي حرف ورقم ورمز
        if len(password) < PASSWORD_MIN_LEN:
            return False
        has_digit = any(c.isdigit() for c in password)
        has_letter = any(c.isalpha() for c in password)
        has_symbol = any(not c.isalnum() for c in password)
        return has_digit and has_letter and has_symbol

    @staticmethod
    def phone_ok(phone: str) -> bool:
        # قاعدة بسيطة: أرقام فقط وطول مقبول (7 إلى 12 رقم)
        return phone.isdigit() and 7 <= len(phone) <= 12

    @staticmethod
    def positive_number(val) -> bool:
        # نتحقق أن val يمكن تحويله إلى float وأنه موجب
        try:
            return float(val) > 0
        except Exception:
            return False

# ---------------------------------------------------------------------
# فئة DataStore: مسؤول عن تحميل وحفظ البيانات في JSON
# ---------------------------------------------------------------------
class DataStore:
    """
    DataStore يحتفظ بالقوائم في الذاكرة (users, cars, invoices)
    ويقوم بتحميلها من الملف وحفظها فيه.
    """
    def __init__(self, path: str = DATA_FILE):
        # مسار ملف البيانات
        self.path = path
        # القوائم في الذاكرة (مبدئيًا فارغة)
        self.users: List[User] = []
        self.cars: List[Car] = []
        self.invoices: List[Invoice] = []
        # محاولة تحميل البيانات من الملف
        self.load()

    def load(self):
        """
        تحميل البيانات من ملف JSON إلى قوائم الكائنات.
        إن لم يوجد الملف، ننشئ واحدًا جديدًا عبر save().
        """
        try:
            # نفتح الملف ونقرأ المحتوى
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # نحول كل dict إلى كائن مطابق
            self.users = [User.from_dict(u) for u in raw.get("users", [])]
            self.cars = [Car.from_dict(c) for c in raw.get("cars", [])]
            self.invoices = [Invoice.from_dict(i) for i in raw.get("invoices", [])]
        except FileNotFoundError:
            # إذا الملف غير موجود ننشئه عبر حفظ الحالة الحالية (الفارغة)
            self.save()

    def save(self):
        """
        حفظ الحالة الحالية إلى ملف JSON. نكتب users, cars, invoices كقوائم dict.
        """
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({
                "users": [u.to_dict() for u in self.users],
                "cars": [c.to_dict() for c in self.cars],
                "invoices": [i.to_dict() for i in self.invoices]
            }, f, indent=2, ensure_ascii=False)

    # -------------------------
    # طرق بحث مساعدة داخل DataStore
    # -------------------------
    def find_user_by_username(self, username: str) -> Optional[User]:
        """البحث عن مستخدم حسب الاسم (username)."""
        return next((u for u in self.users if u.username == username), None)

    def find_user_by_id(self, user_id: str) -> Optional[User]:
        """البحث عن مستخدم حسب المعرف (id)."""
        return next((u for u in self.users if u.id == user_id), None)

    def find_car_by_id(self, car_id: str) -> Optional[Car]:
        """البحث عن سيارة حسب المعرف (id)."""
        return next((c for c in self.cars if c.id == car_id), None)

# ---------------------------------------------------------------------
# فئة LoyaltySystem: نظام حساب نقاط الولاء
# ---------------------------------------------------------------------
class LoyaltySystem:
    """
    نظام نقاط الولاء: تحسب النقاط بناءً على السعر.
    القاعدة الحالية: نقطة واحدة لكل 1000 وحدة عملة.
    """
    @staticmethod
    def points_for_price(price: float) -> int:
        # floor division للحصول على عدد النقاط الكاملة
        return int(price // 1000)

# ---------------------------------------------------------------------
# فئة AuthService: تسجيل المستخدمين وتسجيل الدخول
# ---------------------------------------------------------------------
class AuthService:
    """
    فئة تتعامل مع التسجيل (register) وتسجيل الدخول (login).
    تستخدم DataStore للبحث عن المستخدمين وللحفظ بعد التسجيل.
    """
    def __init__(self, store: DataStore):
        # نخزن مرجع DataStore للعمل معه
        self.store = store

    def register(self, username: str, password: str, usertype: str = "Customer",
                 phone: str = "", gender: str = "M") -> Optional[User]:
        """
        تسجيل مستخدم جديد:
        - التحقق من اسم المستخدم (غير موجود، وصالح)
        - التحقق من قوة كلمة المرور
        - إنشاء الكائن المناسب (Admin / SalesEmployee / Customer)
        - حفظه في DataStore
        """
        # تحقق اسم المستخدم
        if not Validator.username_ok(username):
            print("اسم المستخدم غير صالح (يجب أن يبدأ بحرف ويحتوي أحرف وأرقام فقط وطول >=3).")
            return None
        # عدم تكرار اسم المستخدم
        if self.store.find_user_by_username(username):
            print("اسم المستخدم موجود بالفعل.")
            return None
        # تحقق قوة كلمة المرور
        if not Validator.password_ok(password):
            print(f"كلمة المرور ضعيفة. يجب أن تكون طولها >= {PASSWORD_MIN_LEN} وتحتوي حرفًا، رقمًا ورمزًا.")
            return None
        # تحقق رقم الهاتف إن وُضع
        if phone and not Validator.phone_ok(phone):
            print("رقم الهاتف غير صالح.")
            return None

        # اختيار نوع المستخدم وإنشاؤه
        if usertype == "Admin":
            user = Admin(username, password, phone, gender)
        elif usertype == "SalesEmployee":
            user = SalesEmployee(username, password, phone, gender)
        else:
            user = Customer(username, password, phone, gender)

        # إضافة المستخدم إلى DataStore وحفظ الملف
        self.store.users.append(user)
        self.store.save()
        print(f"تم إنشاء حساب {username} بنجاح كـ {usertype}.")
        return user

    def login(self, username: str, password: str) -> Optional[User]:
        """
        تسجيل الدخول:
        - البحث عن المستخدم
        - مقارنة هاش كلمة المرور
        - التحقق من حالة الحساب
        """
        user = self.store.find_user_by_username(username)
        if not user:
            print("المستخدم غير موجود.")
            return None
        # مقارنة الهاش المخزن مع هاش كلمة المرور المدخلة
        if user.password_hash != HashUtil.hash_password(password):
            print("كلمة المرور خاطئة.")
            return None
        # التحقق إن كان الحساب مفعلًا
        if not user.is_active:
            print("الحساب معطّل. اتصل بالمسؤول.")
            return None
        # نجاح تسجيل الدخول
        print(f"تم تسجيل الدخول كـ {user.username} (نوع: {user.usertype}).")
        return user

# ---------------------------------------------------------------------
# فئة CarService: إدارة السيارات (إضافة، تعديل، حذف، بحث)
# ---------------------------------------------------------------------
class CarService:
    """
    فئة توفر عمليات CRUD على السيارات:
    - add_car: إضافة سيارة جديدة
    - edit_car: تعديل حقل/حقول في سيارة موجودة
    - remove_car: حذف سيارة
    - search: بحث بسيط عن السيارة
    """
    def __init__(self, store: DataStore):
        self.store = store

    def add_car(self, name: str, model_year: int, price: float, color: str, specs: str = "") -> Car:
        """
        إنشاء كائن Car جديد وإضافته إلى DataStore ثم الحفظ.
        """
        car = Car(name, model_year, price, color, specs)
        self.store.cars.append(car)
        self.store.save()
        print(f"تمت إضافة السيارة {car.id}")
        return car

    def edit_car(self, car_id: str, **kwargs) -> bool:
        """
        تعديل خصائص السيارة:
        - نقبل kwargs بحيث تكون أسماء الحقول: name, model_year, price, color, specs, status
        - نتحقق إن الحقل موجود في الكائن Car قبل التعديل
        """
        car = self.store.find_car_by_id(car_id)
        if not car:
            print("السيارة غير موجودة.")
            return False
        # نحدث الحقول المسموح بها فقط
        for k, v in kwargs.items():
            if hasattr(car, k):
                setattr(car, k, v)
        # الحفظ بعد التعديل
        self.store.save()
        print("تم تحديث بيانات السيارة.")
        return True

    def remove_car(self, car_id: str) -> bool:
        """
        حذف السيارة من المخزون (إن وُجدت).
        """
        car = self.store.find_car_by_id(car_id)
        if not car:
            print("السيارة غير موجودة.")
            return False
        self.store.cars.remove(car)
        self.store.save()
        print("تم حذف السيارة.")
        return True

    def search(self, term: str) -> List[Car]:
        """
        بحث بسيط: نبحث بالاسم أو اللون أو المعرف.
        - نعيد قائمة من السيارات التي تطابق المصطلح.
        """
        term = term.lower()
        res = [c for c in self.store.cars if term in c.name.lower() or term in c.color.lower() or term == c.id.lower()]
        return res

# ---------------------------------------------------------------------
# فئة SalesService: تنفيذ عملية البيع وإنشاء الفواتير وتحديث نقاط الولاء
# ---------------------------------------------------------------------
class SalesService:
    """
    فئة تتعامل مع عملية بيع سيارة:
    - التحقق من توفر السيارة
    - حساب النقاط عبر LoyaltySystem
    - إنشاء فاتورة وتخزينها
    - تحديث حالة السيارة إلى 'sold'
    - إضافة النقاط إلى حساب العميل
    """
    def __init__(self, store: DataStore):
        self.store = store

    def buy_car(self, customer_username: str, car_id: str) -> Optional[Invoice]:
        """
        شراء سيارة:
        - نبحث السيارة، نتأكد أنها متاحة
        - نحسب النقاط وننشئ فاتورة
        - نحدث بيانات المستخدم وحالة السيارة ونحفظ
        """
        car = self.store.find_car_by_id(car_id)
        if not car:
            print("السيارة غير موجودة.")
            return None
        if car.status != "available":
            print("السيارة غير متاحة للشراء.")
            return None
        # حساب النقاط
        points = LoyaltySystem.points_for_price(car.price)
        # إنشاء الفاتورة
        inv = Invoice(customer_username, car.id, car.price, points)
        # إضافة الفاتورة إلى المستودع
        self.store.invoices.append(inv)
        # تغيير حالة السيارة إلى مباعة
        car.status = "sold"
        # تحديث نقاط العميل في المستخدم المخزن
        user = self.store.find_user_by_username(customer_username)
        if user:
            user.loyalty_points = user.loyalty_points + points
        # حفظ التغييرات في الملف
        self.store.save()
        print(f"تم بيع السيارة. فاتورة: {inv.id} | نقاط مكتسبة: {points}")
        return inv

# ---------------------------------------------------------------------
# فئة ReportGenerator: إنشاء تقارير ملخصة وبسيطة
# ---------------------------------------------------------------------
class ReportGenerator:
    """
    فئة لتوليد تقارير بسيطة:
    - summary: ملخص النظام (عدد المستخدمين/السيارات/الفواتير/الإيراد الكلي)
    - top_customers_by_points: أعلى العملاء بنقاط الولاء
    - list_sold_cars: استعراض الفواتير (السيارات المباعة)
    """
    def __init__(self, store: DataStore):
        self.store = store

    def summary(self) -> dict:
        """حساب الملخص البسيط للنظام"""
        total_revenue = sum(inv.price for inv in self.store.invoices)  # مجموع أسعار الفواتير
        return {
            "users_count": len(self.store.users),
            "cars_count": len(self.store.cars),
            "invoices_count": len(self.store.invoices),
            "total_revenue": total_revenue
        }

    def top_customers_by_points(self, top_n: int = 5) -> List[User]:
        """إرجاع أعلى العملاء من حيث نقاط الولاء"""
        return sorted(self.store.users, key=lambda u: u.loyalty_points, reverse=True)[:top_n]

    def list_sold_cars(self) -> List[Invoice]:
        """إرجاع جميع الفواتير (التي تمثل السيارات المباعة)"""
        return [inv for inv in self.store.invoices]

# ---------------------------------------------------------------------
# فئة Menu: واجهة سطر الأوامر (CLI) للمستخدمين
# ---------------------------------------------------------------------
class Menu:
    """
    فئة تقدم واجهة نصية للمستخدمين:
    - تعرض شاشة تسجيل الدخول/التسجيل
    - توجه المستخدم لقوائم تناسب صلاحياته
    - تستخدم AuthService, CarService, SalesService, ReportGenerator
    """
    def __init__(self, store: DataStore):
        # حفظ مرجع DataStore
        self.store = store
        # إنشاء خدمات العمل
        self.auth = AuthService(store)
        self.car_service = CarService(store)
        self.sales = SalesService(store)
        self.report = ReportGenerator(store)

    def run(self):
        """
        حلقة البرنامج الأساسية:
        - عند التشغيل نتأكد من وجود Admin واحد على الأقل
        - ثم نعرض القائمة الرئيسية (تسجيل دخول/إنشاء حساب/خروج)
        """
        # إن لم يوجد Admin، نطلب إنشاء واحد (seed)
        if not any(u.usertype == "Admin" for u in self.store.users):
            print("لا يوجد مدير (Admin) في النظام. أنشئ حساب مدير أولًا.")
            while True:
                uname = input("ادخل اسم مستخدم للمدير: ").strip()
                pw = getpass.getpass("ادخل كلمة المرور: ")
                # نتحقق من صحة الاسم وكلمة المرور
                if Validator.username_ok(uname) and Validator.password_ok(pw):
                    # نسجل المدير عبر AuthService
                    self.auth.register(uname, pw, "Admin")
                    break
                else:
                    print("التحقق فشل. حاول مجددًا.")

        # حلقة القوائم الرئيسية
        while True:
            print("\n--- نظام بيع السيارات ---")
            print("1) تسجيل الدخول")
            print("2) إنشاء حساب جديد")
            print("3) خروج")
            choice = input("> ").strip()
            if choice == "1":
                user = self._handle_login()
                if user:
                    # توجيه حسب نوع المستخدم
                    if user.usertype == "Admin":
                        self._admin_menu(user)
                    elif user.usertype == "SalesEmployee":
                        self._sales_employee_menu(user)
                    else:
                        self._customer_menu(user)
            elif choice == "2":
                self._handle_register()
            elif choice == "3":
                print("وداعًا.")
                break
            else:
                print("خيار غير صالح.")

    # -------------------------
    # مساعدة: تسجيل / تسجيل دخول
    # -------------------------
    def _handle_register(self):
        """
        قراءة مدخلات المستخدم للتسجيل ثم استدعاء AuthService.register.
        - نسجل بشكل افتراضي كـ Customer.
        """
        uname = input("اسم المستخدم: ").strip()
        pw = getpass.getpass("كلمة المرور: ")
        phone = input("الهاتف (اختياري): ").strip()
        gender = input("الجنس M/F (افتراضي M): ").strip() or "M"
        # استدعاء الخدمة للتسجيل
        self.auth.register(uname, pw, "Customer", phone, gender)

    def _handle_login(self) -> Optional[User]:
        """
        قراءة اسم المستخدم وكلمة المرور ثم استدعاء AuthService.login.
        نعيد User عند النجاح وإلا None.
        """
        uname = input("اسم المستخدم: ").strip()
        pw = getpass.getpass("كلمة المرور: ")
        return self.auth.login(uname, pw)

    # -------------------------
    # قوائم مدير النظام (Admin)
    # -------------------------
    def _admin_menu(self, admin: User):
        """
        قوائم المدير: إمكانية إضافة مستخدمين بأنواع مختلفة،
        استعراض المستخدمين، تفعيل/تعطيل، حذف، حذف سيارة، عرض تقارير.
        """
        while True:
            print("\n--- قائمة المدير (Admin) ---")
            print("1) إضافة مستخدم (Admin / SalesEmployee / Customer)")
            print("2) استعراض المستخدمين")
            print("3) تفعيل/تعطيل مستخدم")
            print("4) حذف مستخدم")
            print("5) حذف سيارة")
            print("6) تقارير الملخص")
            print("7) خروج")
            ch = input("> ").strip()
            if ch == "1":
                # إضافة مستخدم جديد بأنواعه
                uname = input("اسم المستخدم الجديد: ").strip()
                pw = getpass.getpass("كلمة المرور: ")
                utype = input("نوع المستخدم (Admin/SalesEmployee/Customer): ").strip() or "Customer"
                phone = input("هاتف (اختياري): ").strip()
                self.auth.register(uname, pw, utype, phone)
            elif ch == "2":
                # طباعة تمثيل dict لكل مستخدم (لقراءة سهلة)
                for u in self.store.users:
                    print(u.to_dict())
            elif ch == "3":
                # تفعيل/تعطيل مستخدم حسب اسمه
                uname = input("ادخل اسم المستخدم للتبديل: ").strip()
                u = self.store.find_user_by_username(uname)
                if u:
                    u.is_active = not u.is_active
                    self.store.save()
                    print("تم التبديل.")
                else:
                    print("المستخدم غير موجود.")
            elif ch == "4":
                # حذف مستخدم
                uname = input("اسم المستخدم للحذف: ").strip()
                u = self.store.find_user_by_username(uname)
                if u:
                    self.store.users.remove(u)
                    self.store.save()
                    print("تم الحذف.")
                else:
                    print("غير موجود.")
            elif ch == "5":
                # حذف سيارة
                car_id = input("معرف السيارة للحذف: ").strip()
                self.car_service.remove_car(car_id)
            elif ch == "6":
                # عرض ملخص ونقاط العملاء الأعلى
                s = self.report.summary()
                print("ملخص النظام:", s)
                top = self.report.top_customers_by_points()
                print("أعلى العملاء بالنقاط:", [(u.username, u.loyalty_points) for u in top])
            elif ch == "7":
                # الرجوع للقائمة الرئيسية
                break
            else:
                print("خيار غير صالح.")

    # -------------------------
    # قوائم موظف المبيعات (SalesEmployee)
    # -------------------------
    def _sales_employee_menu(self, emp: User):
        """
        قوائم موظف المبيعات: إضافة سيارة، تعديل، استعراض، بحث.
        (لا يسمح بحذف المستخدمين، هذا من صلاحيات Admin فقط).
        """
        while True:
            print("\n--- قائمة موظف المبيعات ---")
            print("1) إضافة سيارة")
            print("2) تعديل سيارة")
            print("3) استعراض السيارات")
            print("4) بحث")
            print("5) خروج")
            ch = input("> ").strip()
            if ch == "1":
                # قراءة بيانات السيارة مع حماية تحويلات الأرقام
                name = input("اسم السيارة: ").strip()
                try:
                    model = int(input("سنة الموديل (مثال: 2020): ").strip())
                    price = float(input("السعر: ").strip())
                except Exception:
                    print("خطأ: تحقق من الأرقام.")
                    continue
                color = input("اللون: ").strip()
                specs = input("مواصفات (اختياري): ").strip()
                self.car_service.add_car(name, model, price, color, specs)
            elif ch == "2":
                # تعديل سيارة: نحدد المعرف ثم الحقل والقيمة
                cid = input("معرف السيارة للتعديل: ").strip()
                key = input("الحقل للتعديل (name/model_year/price/color/specs/status): ").strip()
                val = input("القيمة الجديدة: ").strip()
                kwargs = {}
                # تحويل القيم العددية للحقل المناسب
                if key in ("model_year",):
                    try:
                        kwargs[key] = int(val)
                    except:
                        print("قيمة غير صحيحة للسنة.")
                        continue
                elif key in ("price",):
                    try:
                        kwargs[key] = float(val)
                    except:
                        print("قيمة سعر غير صحيحة.")
                        continue
                else:
                    kwargs[key] = val
                self.car_service.edit_car(cid, **kwargs)
            elif ch == "3":
                # طباعة تمثيل كل سيارة
                for c in self.store.cars:
                    print(c.to_dict())
            elif ch == "4":
                # بحث بواسطة مصطلح
                t = input("مصطلح البحث (اسم/لون/معرف): ").strip()
                res = self.car_service.search(t)
                for r in res:
                    print(r.to_dict())
            elif ch == "5":
                break
            else:
                print("خيار غير صالح.")

    # -------------------------
    # قوائم العميل (Customer)
    # -------------------------
    def _customer_menu(self, cust: User):
        """
        قوائم العميل: تصفح السيارات المتاحة، بحث، شراء، عرض الفواتير الخاصة به.
        """
        while True:
            print("\n--- قائمة العميل ---")
            print("1) تصفح السيارات المتاحة")
            print("2) بحث عن سيارة")
            print("3) شراء سيارة")
            print("4) عرض فواتيري")
            print("5) خروج")
            ch = input("> ").strip()
            if ch == "1":
                # عرض السيارات المتاحة فقط
                for c in self.store.cars:
                    if c.status == "available":
                        print(c.to_dict())
            elif ch == "2":
                # بحث
                t = input("مصطلح البحث: ").strip()
                res = self.car_service.search(t)
                for r in res:
                    print(r.to_dict())
            elif ch == "3":
                # شراء سيارة: نأخذ معرف السيارة من العميل وننفّذ عملية الشراء
                cid = input("معرف السيارة للشراء: ").strip()
                # نستخدم اسم المستخدم من كائن cust (الذي تم تسجيل الدخول به)
                inv = self.sales.buy_car(cust.username, cid)
                if inv:
                    print("تم الشراء. فاتورة:", inv.to_dict())
            elif ch == "4":
                # عرض جميع الفواتير التي تخص هذا العميل
                for inv in self.store.invoices:
                    if inv.customer == cust.username:
                        print(inv.to_dict())
            elif ch == "5":
                break
            else:
                print("خيار غير صالح.")

# ---------------------------------------------------------------------
# نقطة الانطلاق (main)
# ---------------------------------------------------------------------
def main():
    """
    الدالة الرئيسية: تنشئ DataStore ثم Menu وتبدأ التشغيل.
    """
    store = DataStore()
    menu = Menu(store)
    menu.run()

# عند تشغيل الملف مباشرة، نستدعي main()
if __name__ == "__main__":
    main()
