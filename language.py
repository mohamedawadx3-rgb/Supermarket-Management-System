# ============================================================
# الملف: language.py
# الوظيفة: إدارة لغات البرنامج وحفظ اللغة المختارة
# ============================================================

import json
import os


# قاموس الكلمات والترجمات الأساسية
TRANSLATIONS = {
    "Dashboard": "لوحة التحكم",
    "Products": "المنتجات",
    "Categories": "الفئات",
    "Sales": "المبيعات",
    "Customers": "العملاء",
    "Suppliers": "الموردين",
    "Inventory": "المخزون",
    "Reports": "التقارير",
    "Settings": "الإعدادات",
    "MAIN MENU": "القائمة الرئيسية",
    "Management System": "نظام الإدارة",
    "Version 1.0": "الإصدار 1.0",
    "Application Name": "اسم البرنامج",
    "Application Version": "إصدار البرنامج",
    "Database Name": "اسم قاعدة البيانات",
    "System Actions": "إعدادات النظام",
    "Application Language": "لغة البرنامج",
    "Test Database Connection": "اختبار اتصال قاعدة البيانات",
    "Refresh Current Page": "تحديث الصفحة الحالية",
    "About System": "عن البرنامج",
    "System Settings": "إعدادات النظام",
    "Manage and view system information": "إدارة وعرض معلومات النظام",
}


class LanguageManager:

    def __init__(self):

        # تحديد مكان ملف حفظ اللغة
        self.file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "language.json"
        )

        # اللغة الافتراضية
        self.language = "English"

        # تحميل اللغة المحفوظة
        self.load_language()

    # تحميل اللغة من ملف الإعدادات
    def load_language(self):

        try:
            if os.path.exists(self.file_path):

                with open(self.file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                    saved_language = data.get("language", "English")

                    if saved_language in ["English", "العربية"]:
                        self.language = saved_language

        except (OSError, json.JSONDecodeError):
            self.language = "English"

    # حفظ اللغة المختارة
    def set_language(self, language):

        if language not in ["English", "العربية"]:
            return

        self.language = language

        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(
                    {"language": language},
                    file,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError:
            print("Could not save language settings.")

    # إرجاع اللغة الحالية
    def get_language(self):
        return self.language

    # ترجمة النص
    def translate(self, english, arabic=None):

        if self.language == "English":
            return english

        if arabic is not None:
            return arabic

        return TRANSLATIONS.get(english, english)