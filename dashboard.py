# ============================================================
# مشروع Supermarket Management System
# الملف: dashboard.py
# الوظيفة: إنشاء لوحة التحكم وعرض إحصائيات السوبر ماركت
# ============================================================

import customtkinter as ctk
from datetime import datetime


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent, db, app):

        super().__init__(parent, fg_color="transparent")

        self.db = db
        self.app = app
        self.colors = self.app.colors

        self.create_dashboard()

    # ========================================================
    # دالة الترجمة
    # ========================================================

    def t(self, english, arabic):
        return self.app.t(english, arabic)

    # ========================================================
    # إنشاء لوحة التحكم
    # ========================================================

    def create_dashboard(self):

        # عنوان لوحة التحكم
        ctk.CTkLabel(
            self,
            text=self.t("Welcome to Dashboard", "مرحباً بك في لوحة التحكم"),
            font=("Arial", 25, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=(5, 5))

        # وصف لوحة التحكم
        ctk.CTkLabel(
            self,
            text=self.t(
                "Here's an overview of your supermarket",
                "نظرة عامة على السوبر ماركت"
            ),
            font=("Arial", 13),
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", pady=(0, 20))

        # قراءة الإحصائيات من قاعدة البيانات
        statistics = self.get_statistics()

        # إطار بطاقات الإحصائيات
        cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        cards_frame.pack(fill="x", pady=(0, 20))

        for column in range(4):
            cards_frame.grid_columnconfigure(column, weight=1)

        # بطاقة إجمالي المنتجات
        self.create_stat_card(
            cards_frame,
            "Total Products",
            "إجمالي المنتجات",
            statistics["products"],
            "Number of registered products",
            "عدد المنتجات المسجلة",
            0
        )

        # بطاقة المخزون
        self.create_stat_card(
            cards_frame,
            "Stock Quantity",
            "كمية المخزون",
            statistics["stock"],
            "Total items in inventory",
            "إجمالي الكميات في المخزون",
            1
        )

        # بطاقة العملاء
        self.create_stat_card(
            cards_frame,
            "Total Customers",
            "إجمالي العملاء",
            statistics["customers"],
            "Registered customers",
            "عدد العملاء المسجلين",
            2
        )

        # بطاقة المبيعات الشهرية
        self.create_stat_card(
            cards_frame,
            "Monthly Sales",
            "مبيعات الشهر",
            self.format_money(statistics["sales"]),
            "Sales during this month",
            "المبيعات خلال الشهر الحالي",
            3
        )

        # عنوان آخر المبيعات
        ctk.CTkLabel(
            self,
            text=self.t("Recent Sales", "أحدث المبيعات"),
            font=("Arial", 20, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=(5, 12))

        # إطار عرض آخر الفواتير
        self.recent_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["card"],
            corner_radius=12
        )
        self.recent_frame.pack(fill="both", expand=True)

        self.create_sales_headers()
        self.display_recent_sales(statistics["recent_sales"])

    # ========================================================
    # قراءة الإحصائيات من قاعدة البيانات
    # ========================================================

    def get_statistics(self):

        statistics = {
            "products": 0,
            "stock": 0,
            "customers": 0,
            "sales": 0,
            "recent_sales": []
        }

        connection = None
        cursor = None

        try:

            connection = self.db.get_connection()
            cursor = connection.cursor()

            # حساب عدد المنتجات
            cursor.execute("SELECT COUNT(*) FROM products")
            statistics["products"] = cursor.fetchone()[0]

            # حساب إجمالي المخزون
            cursor.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM products"
            )
            statistics["stock"] = cursor.fetchone()[0]

            # حساب عدد العملاء
            cursor.execute("SELECT COUNT(*) FROM customers")
            statistics["customers"] = cursor.fetchone()[0]

            # حساب مبيعات الشهر الحالي
            cursor.execute(
                """
                SELECT COALESCE(SUM(total), 0)
                FROM sales
                WHERE YEAR(sale_date) = YEAR(CURDATE())
                AND MONTH(sale_date) = MONTH(CURDATE())
                """
            )
            statistics["sales"] = cursor.fetchone()[0]

            # جلب آخر خمس فواتير
            cursor.execute(
                """
                SELECT sale_id, total, sale_date, payment_method
                FROM sales
                ORDER BY sale_id DESC
                LIMIT 5
                """
            )
            statistics["recent_sales"] = cursor.fetchall()

        except Exception as error:
            print("Dashboard Database Error:", error)

        finally:

            if cursor is not None:
                cursor.close()

            if connection is not None and connection.is_connected():
                connection.close()

        return statistics

    # ========================================================
    # إنشاء بطاقة إحصائية
    # ========================================================

    def create_stat_card(
        self,
        parent,
        title_en,
        title_ar,
        value,
        description_en,
        description_ar,
        column
    ):

        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=12,
            height=145
        )

        card.grid(
            row=0,
            column=column,
            padx=6,
            pady=5,
            sticky="nsew"
        )

        card.grid_propagate(False)

        # عنوان البطاقة
        ctk.CTkLabel(
            card,
            text=self.t(title_en, title_ar),
            font=("Arial", 13),
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", padx=15, pady=(17, 5))

        # القيمة الرئيسية
        ctk.CTkLabel(
            card,
            text=str(value),
            font=("Arial", 24, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", padx=15, pady=3)

        # وصف البطاقة
        ctk.CTkLabel(
            card,
            text=self.t(description_en, description_ar),
            font=("Arial", 10),
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", padx=15, pady=(3, 10))

    # ========================================================
    # إنشاء عناوين جدول آخر المبيعات
    # ========================================================

    def create_sales_headers(self):

        header_frame = ctk.CTkFrame(
            self.recent_frame,
            fg_color="#273449",
            corner_radius=8
        )

        header_frame.pack(fill="x", padx=12, pady=(12, 5))

        for column, weight in enumerate([1, 1, 2, 1]):
            header_frame.grid_columnconfigure(column, weight=weight)

        headers = [
            ("Invoice ID", "رقم الفاتورة"),
            ("Total", "الإجمالي"),
            ("Date", "التاريخ"),
            ("Payment", "طريقة الدفع")
        ]

        for column, (english, arabic) in enumerate(headers):

            ctk.CTkLabel(
                header_frame,
                text=self.t(english, arabic),
                font=("Arial", 12, "bold"),
                text_color=self.colors["text"]
            ).grid(
                row=0,
                column=column,
                padx=8,
                pady=12,
                sticky="w"
            )

    # ========================================================
    # عرض آخر خمس فواتير
    # ========================================================

    def display_recent_sales(self, sales):

        if not sales:

            ctk.CTkLabel(
                self.recent_frame,
                text=self.t(
                    "No sales records found yet.",
                    "لا توجد فواتير مبيعات حتى الآن."
                ),
                font=("Arial", 13),
                text_color=self.colors["secondary_text"]
            ).pack(pady=35)

            return

        for sale in sales:

            row_frame = ctk.CTkFrame(
                self.recent_frame,
                fg_color="transparent"
            )
            row_frame.pack(fill="x", padx=12, pady=5)

            for column, weight in enumerate([1, 1, 2, 1]):
                row_frame.grid_columnconfigure(column, weight=weight)

            # قراءة بيانات الفاتورة
            sale_id = sale[0]
            total = self.format_money(sale[1])
            sale_date = sale[2]
            payment_method = sale[3]

            # تنسيق التاريخ
            if hasattr(sale_date, "strftime"):
                sale_date = sale_date.strftime("%d-%m-%Y")

            values = [
                f"#{sale_id}",
                total,
                str(sale_date),
                str(payment_method)
            ]

            # عرض بيانات الفاتورة
            for column, value in enumerate(values):

                ctk.CTkLabel(
                    row_frame,
                    text=value,
                    font=("Arial", 12),
                    text_color=self.colors["text"]
                ).grid(
                    row=0,
                    column=column,
                    padx=8,
                    pady=10,
                    sticky="w"
                )

            # خط فاصل بين الفواتير
            ctk.CTkFrame(
                self.recent_frame,
                height=1,
                fg_color=self.colors["border"]
            ).pack(fill="x", padx=15)

    # ========================================================
    # تنسيق المبالغ المالية
    # ========================================================

    def format_money(self, amount):

        amount = float(amount or 0)
        return f"{amount:,.2f} EGP"