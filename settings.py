# ============================================================
# مشروع Supermarket Management System
# الملف: settings.py
# الوظيفة: إعدادات البرنامج وتغيير اللغة
# ============================================================

import customtkinter as ctk
from tkinter import messagebox


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color="transparent")

        self.db = db
        self.app = app
        self.colors = app.colors

        self.create_interface()

    # ========================================================
    # دالة الترجمة
    # ========================================================

    def t(self, english, arabic):
        return self.app.t(english, arabic)

    # ========================================================
    # إنشاء واجهة الإعدادات
    # ========================================================

    def create_interface(self):

        # عنوان الصفحة
        ctk.CTkLabel(
            self,
            text=self.t("System Settings", "إعدادات النظام"),
            font=("Arial", 25, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", padx=20, pady=(20, 5))

        # وصف الصفحة
        ctk.CTkLabel(
            self,
            text=self.t(
                "Manage and view system information",
                "إدارة وعرض معلومات النظام"
            ),
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # إطار معلومات النظام
        info_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["card"]
        )
        info_frame.pack(fill="x", padx=20, pady=10)

        # اسم النظام
        ctk.CTkLabel(
            info_frame,
            text=self.t("Application Name", "اسم البرنامج"),
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 3))

        ctk.CTkLabel(
            info_frame,
            text="Supermarket Management System",
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # إصدار البرنامج
        ctk.CTkLabel(
            info_frame,
            text=self.t("Application Version", "إصدار البرنامج"),
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=20, pady=3)

        ctk.CTkLabel(
            info_frame,
            text="Version 1.0",
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # اسم قاعدة البيانات
        ctk.CTkLabel(
            info_frame,
            text=self.t("Database Name", "اسم قاعدة البيانات"),
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=20, pady=3)

        ctk.CTkLabel(
            info_frame,
            text="supermarket_system",
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # إطار خيارات البرنامج
        actions_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["card"]
        )
        actions_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            actions_frame,
            text=self.t("System Actions", "إعدادات النظام"),
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=20, pady=15)

        # اختيار لغة البرنامج
        ctk.CTkLabel(
            actions_frame,
            text=self.t("Application Language", "لغة البرنامج"),
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(5, 7))

        self.language_menu = ctk.CTkOptionMenu(
            actions_frame,
            values=["English", "العربية"],
            width=180,
            command=self.change_language
        )
        self.language_menu.pack(anchor="w", padx=20, pady=(0, 15))

        # عرض اللغة المحفوظة
        self.language_menu.set(self.app.language)

        # اختبار الاتصال بقاعدة البيانات
        ctk.CTkButton(
            actions_frame,
            text=self.t(
                "Test Database Connection",
                "اختبار اتصال قاعدة البيانات"
            ),
            command=self.test_connection,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"]
        ).pack(anchor="w", padx=20, pady=7)

        # تحديث الصفحة
        ctk.CTkButton(
            actions_frame,
            text=self.t(
                "Refresh Current Page",
                "تحديث الصفحة الحالية"
            ),
            command=self.refresh_page,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"]
        ).pack(anchor="w", padx=20, pady=7)

        # معلومات البرنامج
        ctk.CTkButton(
            actions_frame,
            text=self.t("About System", "عن البرنامج"),
            command=self.show_about,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"]
        ).pack(anchor="w", padx=20, pady=(7, 20))

        # حقوق المشروع
        ctk.CTkLabel(
            self,
            text=self.t(
                "Supermarket Management System | 2026",
                "نظام إدارة السوبر ماركت | 2026"
            ),
            text_color=self.colors["secondary_text"],
            font=("Arial", 12)
        ).pack(pady=20)

    # ========================================================
    # تغيير لغة البرنامج
    # ========================================================

    def change_language(self, selected_language):

        # استخدام دالة التطبيق الرئيسية لحفظ وتغيير اللغة
        self.app.change_language(selected_language)

    # ========================================================
    # اختبار الاتصال بقاعدة البيانات
    # ========================================================

    def test_connection(self):

        connection = None

        try:
            connection = self.db.get_connection()

            if connection and connection.is_connected():
                messagebox.showinfo(
                    self.t("Connection Successful", "تم الاتصال بنجاح"),
                    self.t(
                        "Database connection is working correctly.",
                        "الاتصال بقاعدة البيانات يعمل بشكل صحيح."
                    )
                )
            else:
                messagebox.showerror(
                    self.t("Connection Error", "خطأ في الاتصال"),
                    self.t(
                        "Could not connect to the database.",
                        "تعذر الاتصال بقاعدة البيانات."
                    )
                )

        except Exception as error:
            messagebox.showerror(
                self.t("Connection Error", "خطأ في الاتصال"),
                str(error)
            )

        finally:
            if connection:
                try:
                    if connection.is_connected():
                        connection.close()
                except Exception:
                    pass

    # ========================================================
    # تحديث صفحة الإعدادات
    # ========================================================

    def refresh_page(self):
        self.app.show_page("Settings")

    # ========================================================
    # عرض معلومات البرنامج
    # ========================================================

    def show_about(self):

        messagebox.showinfo(
            self.t("About System", "عن البرنامج"),
            self.t(
                "Supermarket Management System\n\n"
                "A desktop application built using Python, "
                "CustomTkinter and MySQL.\n\n"
                "Version 1.0",
                "نظام إدارة السوبر ماركت\n\n"
                "تطبيق سطح مكتب تم إنشاؤه باستخدام "
                "Python و CustomTkinter و MySQL.\n\n"
                "الإصدار 1.0"
            )
        )