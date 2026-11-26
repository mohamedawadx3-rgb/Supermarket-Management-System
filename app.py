# ============================================================
# مشروع Supermarket Management System
# الملف: app.py
# الوظيفة: الواجهة الرئيسية والتحكم في التنقل واللغة
# ============================================================

# مكتبة إنشاء الواجهات الرسومية
import customtkinter as ctk

# مكتبة رسائل التنبيه والتأكيد والأخطاء
from tkinter import messagebox

# مكتبة التعامل مع التاريخ والوقت
from datetime import datetime

# مكتبة استيراد ملفات الأقسام تلقائيًا
import importlib

# مكتبات معالجة وعرض النصوص العربية
import arabic_reshaper
from bidi.algorithm import get_display

# استيراد كلاس قاعدة البيانات
from database import Database

# استيراد مدير اللغات
from language import LanguageManager


# إعداد شكل التطبيق
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# الكلاس الرئيسي للبرنامج
class SupermarketApp(ctk.CTk):

    # ========================================================
    # إنشاء التطبيق الرئيسي
    # ========================================================

    def __init__(self):

        # تهيئة النافذة الرئيسية
        super().__init__()

        # إنشاء مدير اللغة وقراءة اللغة المحفوظة
        self.language_manager = LanguageManager()
        self.language = self.language_manager.get_language()

        # تحديد عنوان النافذة (نص خام لأن شريط ويندوز يعالج العربي بنفسه)
        self.title(self.raw_t(
            "Supermarket Management System",
            "نظام إدارة السوبر ماركت"
        ))

        # تحديد حجم النافذة
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # تحديد لون خلفية التطبيق
        self.configure(fg_color="#111827")

        # إنشاء الاتصال بقاعدة البيانات
        self.db = Database()

        # التأكد من جاهزية قاعدة البيانات
        self.database_ready = self.db.initialize_database()

        # إظهار تحذير في حالة عدم الاتصال بقاعدة البيانات
        if not self.database_ready:

            messagebox.showwarning(
                self.raw_t("Database Warning", "تحذير قاعدة البيانات"),
                self.raw_t(
                    "Could not connect to the database.\n"
                    "Please check that MySQL is running in XAMPP.",
                    "تعذر الاتصال بقاعدة البيانات.\n"
                    "تأكد من تشغيل MySQL في XAMPP."
                )
            )

        # ألوان التصميم المستخدمة في جميع الصفحات
        self.colors = {
            "background": "#111827",
            "sidebar": "#0B1220",
            "card": "#1F2937",
            "primary": "#2563EB",
            "primary_hover": "#1D4ED8",
            "text": "#F9FAFB",
            "secondary_text": "#9CA3AF",
            "border": "#374151",
            "success": "#10B981",
            "danger": "#EF4444"
        }

        # تحديد الأقسام الموجودة داخل البرنامج
        self.pages = {

            "Dashboard": {
                "title": "Dashboard",
                "module": "dashboard",
                "class": "DashboardPage"
            },

            "Products": {
                "title": "Products Management",
                "module": "products",
                "class": "ProductsPage"
            },

            "Categories": {
                "title": "Categories Management",
                "module": "categories",
                "class": "CategoriesPage"
            },

            "Sales": {
                "title": "Sales Management",
                "module": "sales",
                "class": "SalesPage"
            },

            "Customers": {
                "title": "Customers Management",
                "module": "customers",
                "class": "CustomersPage"
            },

            "Suppliers": {
                "title": "Suppliers Management",
                "module": "suppliers",
                "class": "SuppliersPage"
            },

            "Inventory": {
                "title": "Inventory Management",
                "module": "inventory",
                "class": "InventoryPage"
            },

            "Reports": {
                "title": "Reports",
                "module": "reports",
                "class": "ReportsPage"
            },

            "Settings": {
                "title": "Settings",
                "module": "settings",
                "class": "SettingsPage"
            }
        }

        # حفظ بيانات القسم المحدد حاليًا
        self.active_button = None
        self.current_page = None
        self.current_page_name = "Dashboard"

        # إنشاء شكل التطبيق الرئيسي
        self.create_main_layout()

        # فتح لوحة التحكم عند تشغيل البرنامج
        self.show_page("Dashboard")

    # ========================================================
    # ترجمة النصوص مع معالجة اتجاه العربي
    # (لعناصر الواجهة المرسومة بواسطة Tk فقط)
    # ========================================================

    def t(self, english, arabic=None):

        # الحصول على النص المترجم من مدير اللغة
        text = self.language_manager.translate(english, arabic)

        # معالجة النص العربي حتى يظهر بشكل صحيح في عناصر الواجهة
        if self.language == "العربية":

            text = arabic_reshaper.reshape(text)
            text = get_display(text)

        # إرجاع النص بعد الترجمة والمعالجة
        return text

    # ========================================================
    # ترجمة النصوص بدون معالجة اتجاه الحروف
    # (لرسائل messagebox وعنوان النافذة)
    # ========================================================

    def raw_t(self, english, arabic=None):

        # الحصول على النص المترجم فقط
        # بدون إعادة تشكيل الحروف أو تغيير اتجاهها
        return self.language_manager.translate(english, arabic)

    # ========================================================
    # تغيير لغة البرنامج
    # ========================================================

    def change_language(self, selected_language):

        # حفظ اللغة الجديدة في ملف اللغة
        self.language_manager.set_language(selected_language)

        # تحديث اللغة المستخدمة داخل البرنامج
        self.language = self.language_manager.get_language()

        # تحديث عنوان النافذة باللغة الجديدة (نص خام)
        self.title(self.raw_t(
            "Supermarket Management System",
            "نظام إدارة السوبر ماركت"
        ))

        # حذف محتويات القائمة الجانبية القديمة
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        # إعادة إنشاء القائمة الجانبية باللغة الجديدة
        self.create_sidebar()

        # إعادة فتح القسم الحالي باللغة الجديدة
        self.show_page(self.current_page_name)

    # ========================================================
    # إنشاء الهيكل الأساسي للتطبيق
    # ========================================================

    def create_main_layout(self):

        # إنشاء القائمة الجانبية
        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=self.colors["sidebar"]
        )

        # وضع القائمة الجانبية على الشمال
        self.sidebar.pack(side="left", fill="y")

        # تثبيت عرض القائمة الجانبية
        self.sidebar.pack_propagate(False)

        # إنشاء المساحة الرئيسية
        self.main_area = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.colors["background"]
        )

        # وضع المساحة الرئيسية بجانب القائمة
        self.main_area.pack(
            side="right",
            fill="both",
            expand=True
        )

        # إنشاء الشريط العلوي
        self.create_header()

        # إنشاء الإطار الذي ستظهر بداخله صفحات البرنامج
        self.content_frame = ctk.CTkFrame(
            self.main_area,
            fg_color="transparent"
        )

        # وضع إطار الصفحات داخل المساحة الرئيسية
        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        # إنشاء القائمة الجانبية
        self.create_sidebar()
        # ========================================================
    # إنشاء القائمة الجانبية
    # ========================================================

    def create_sidebar(self):

        # إنشاء إطار الشعار
        self.logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        self.logo_frame.pack(
            fill="x",
            padx=15,
            pady=(25, 30)
        )

        # عرض اسم المشروع
        ctk.CTkLabel(
            self.logo_frame,
            text="SUPERMARKET",
            font=("Arial", 20, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w")

        # عرض وصف المشروع
        ctk.CTkLabel(
            self.logo_frame,
            text=self.t("Management System", "نظام الإدارة"),
            font=("Arial", 11),
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", pady=(4, 0))

        # عنوان القائمة الرئيسية
        ctk.CTkLabel(
            self.sidebar,
            text=self.t("MAIN MENU", "القائمة الرئيسية"),
            font=("Arial", 11, "bold"),
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # أسماء الأقسام
        menu_items = [
            "Dashboard",
            "Products",
            "Categories",
            "Sales",
            "Customers",
            "Suppliers",
            "Inventory",
            "Reports",
            "Settings"
        ]

        # أسماء الأقسام باللغة العربية
        arabic_names = {
            "Dashboard": "لوحة التحكم",
            "Products": "المنتجات",
            "Categories": "الفئات",
            "Sales": "المبيعات",
            "Customers": "العملاء",
            "Suppliers": "الموردين",
            "Inventory": "المخزون",
            "Reports": "التقارير",
            "Settings": "الإعدادات"
        }

        # إنشاء زر لكل قسم
        for item in menu_items:

            button = ctk.CTkButton(
                self.sidebar,

                # ترجمة اسم القسم
                text=self.t(item, arabic_names[item]),

                height=42,
                corner_radius=8,
                anchor="w",
                font=("Arial", 14),
                fg_color="transparent",
                hover_color=self.colors["card"],
                text_color=self.colors["secondary_text"],

                # فتح القسم عند الضغط على الزر
                command=lambda page=item: self.show_page(page)
            )

            # وضع الزر داخل القائمة الجانبية
            button.pack(fill="x", padx=12, pady=3)

            # حفظ الزر للوصول إليه لاحقًا
            setattr(self, f"button_{item}", button)

        # عرض إصدار البرنامج أسفل القائمة
        ctk.CTkLabel(
            self.sidebar,
            text=self.t("Version 1.0", "الإصدار 1.0"),
            font=("Arial", 10),
            text_color=self.colors["secondary_text"]
        ).pack(side="bottom", pady=20)

    # ========================================================
    # إنشاء الشريط العلوي
    # ========================================================

    def create_header(self):

        # إنشاء إطار الشريط العلوي
        self.header = ctk.CTkFrame(
            self.main_area,
            height=75,
            corner_radius=0,
            fg_color=self.colors["card"]
        )

        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        # إنشاء إطار يحتوي على بيانات الشريط العلوي
        header_content = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        header_content.pack(
            fill="both",
            expand=True,
            padx=25
        )

        # عنوان الصفحة الحالية
        self.page_title = ctk.CTkLabel(
            header_content,
            text=self.t("Dashboard", "لوحة التحكم"),
            font=("Arial", 21, "bold"),
            text_color=self.colors["text"]
        )

        self.page_title.pack(side="left", pady=20)

        # الحصول على التاريخ الحالي
        current_date = datetime.now().strftime("%d-%m-%Y")

        # عرض التاريخ داخل الشريط العلوي
        self.date_label = ctk.CTkLabel(
            header_content,
            text=current_date,
            font=("Arial", 12),
            text_color=self.colors["secondary_text"]
        )

        self.date_label.pack(side="right", pady=20)

    # ========================================================
    # تحديث شكل الزر المحدد في القائمة الجانبية
    # ========================================================

    def update_active_button(self, selected_page):

        # المرور على جميع الأقسام
        for page_name in self.pages:

            # الحصول على زر القسم
            button = getattr(self, f"button_{page_name}")

            # تمييز القسم المفتوح حاليًا
            if page_name == selected_page:

                button.configure(
                    fg_color=self.colors["primary"],
                    hover_color=self.colors["primary_hover"],
                    text_color="#FFFFFF"
                )

            else:

                # إعادة شكل الأزرار غير المحددة
                button.configure(
                    fg_color="transparent",
                    hover_color=self.colors["card"],
                    text_color=self.colors["secondary_text"]
                )

    # ========================================================
    # فتح القسم المطلوب
    # ========================================================

    def show_page(self, page_name):

        # التأكد من أن القسم المطلوب موجود
        if page_name not in self.pages:

            messagebox.showerror(
                self.raw_t("Error", "خطأ"),
                self.raw_t(
                    "The selected page does not exist.",
                    "القسم المحدد غير موجود."
                )
            )

            return

        # حفظ اسم القسم الحالي
        self.current_page_name = page_name

        # الحصول على بيانات القسم
        page_info = self.pages[page_name]

        # أسماء الأقسام باللغة العربية
        arabic_titles = {
            "Dashboard": "لوحة التحكم",
            "Products": "إدارة المنتجات",
            "Categories": "إدارة الفئات",
            "Sales": "إدارة المبيعات",
            "Customers": "إدارة العملاء",
            "Suppliers": "إدارة الموردين",
            "Inventory": "إدارة المخزون",
            "Reports": "التقارير",
            "Settings": "الإعدادات"
        }

        # تحديث عنوان الصفحة في الشريط العلوي
        self.page_title.configure(
            text=self.t(
                page_info["title"],
                arabic_titles[page_name]
            )
        )

        # تحديث الزر المحدد في القائمة
        self.update_active_button(page_name)

        # حذف محتويات الصفحة القديمة
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        try:

            # استيراد ملف القسم المطلوب
            module = importlib.import_module(page_info["module"])

            # الحصول على كلاس الصفحة من الملف
            page_class = getattr(module, page_info["class"])

            # إنشاء الصفحة وإرسال قاعدة البيانات والتطبيق الرئيسي إليها
            self.current_page = page_class(
                self.content_frame,
                self.db,
                self
            )

            # عرض الصفحة داخل إطار المحتوى
            self.current_page.pack(
                fill="both",
                expand=True
            )

        except ModuleNotFoundError:

            # إظهار رسالة إذا كان ملف القسم غير موجود
            messagebox.showwarning(
                self.raw_t("Page Not Ready", "القسم غير جاهز"),
                self.raw_t(
                    f"The file for {page_name} has not been created yet.",
                    f"ملف قسم {arabic_titles[page_name]} غير موجود."
                )
            )

        except AttributeError:

            # إظهار رسالة إذا كان كلاس الصفحة غير موجود
            messagebox.showerror(
                self.raw_t("Page Error", "خطأ في القسم"),
                self.raw_t(
                    "The required class was not found.",
                    "الكلاس المطلوب غير موجود."
                )
            )

        except Exception as error:

            # إظهار رسالة في حالة حدوث خطأ أثناء فتح القسم
            messagebox.showerror(
                self.raw_t("Application Error", "خطأ في البرنامج"),
                self.raw_t(
                    f"An error occurred while opening {page_name}:\n{error}",
                    f"حدث خطأ أثناء فتح القسم:\n{error}"
                )
            )