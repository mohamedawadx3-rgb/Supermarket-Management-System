import customtkinter as ctk  # مكتبة تصميم الواجهة بشكل حديث
from tkinter import ttk, messagebox  # مكتبة الجداول ورسائل التنبيه والتأكيد
from mysql.connector import Error  # التعامل مع أخطاء الاتصال وقاعدة بيانات MySQL


class ReportsPage(ctk.CTkFrame):  # إنشاء صفحة التقارير والإحصائيات

    def __init__(self, parent, db, app):  # استقبال الإطار الأب وقاعدة البيانات والتطبيق الرئيسي
        super().__init__(parent, fg_color="transparent")  # تهيئة الصفحة وجعل خلفيتها شفافة

        self.db = db  # حفظ كائن قاعدة البيانات لاستخدامه في تنفيذ الاستعلامات
        self.app = app  # حفظ التطبيق الرئيسي لاستخدام دواله، ومنها دالة الترجمة
        self.colors = app.colors  # الحصول على ألوان التصميم الموحدة للبرنامج

        self.create_interface()  # إنشاء جميع عناصر واجهة التقارير
        self.load_reports()  # تحميل الإحصائيات والبيانات وعرضها داخل الصفحة

    # دالة مختصرة لترجمة النصوص حسب اللغة المختارة في البرنامج
    def t(self, english, arabic=None):
        return self.app.t(english, arabic)  # إرسال النص إلى دالة الترجمة الموجودة في app.py

    # دالة ترجمة النصوص بدون معالجة اتجاه العربية
    def raw_t(self, english, arabic):
        return self.app.raw_t(english, arabic)

    def create_interface(self):  # دالة إنشاء واجهة التقارير والإحصائيات

        # إنشاء عنوان الصفحة الرئيسي
        ctk.CTkLabel(
            self,
            text=self.t("Reports & Statistics", "التقارير والإحصائيات"),  # ترجمة عنوان الصفحة
            font=("Arial", 25, "bold"),  # تحديد نوع الخط وحجمه وجعله عريضًا
            text_color=self.colors["text"]  # استخدام لون النص الأساسي
        ).pack(anchor="w", padx=20, pady=(15, 3))  # وضع العنوان ناحية اليسار مع تحديد المسافات

        # إنشاء وصف مختصر يوضح وظيفة صفحة التقارير
        ctk.CTkLabel(
            self,
            text=self.t(
                "View sales, expenses and inventory statistics",
                "عرض إحصائيات المبيعات والمصروفات والمخزون"
            ),
            text_color=self.colors["secondary_text"]  # استخدام لون النص الثانوي
        ).pack(anchor="w", padx=20, pady=(0, 15))  # تحديد مكان الوصف والمسافات حوله

        # إنشاء إطار يجمع بطاقات الإحصائيات الثلاث
        self.stats_frame = ctk.CTkFrame(
            self, fg_color="transparent"  # جعل خلفية الإطار شفافة
        )
        self.stats_frame.pack(fill="x", padx=15, pady=10)  # تمديد الإطار أفقيًا وإضافة مسافات

        # إنشاء متغيرات نصية لحفظ الأرقام التي ستظهر داخل البطاقات
        self.sales_value = ctk.StringVar(value="0.00")  # متغير يعرض إجمالي المبيعات
        self.expenses_value = ctk.StringVar(value="0.00")  # متغير يعرض إجمالي المصروفات
        self.invoices_value = ctk.StringVar(value="0")  # متغير يعرض عدد الفواتير

        # إنشاء بطاقة إجمالي المبيعات
        self.create_stat_card(
            self.stats_frame,
            self.t("Total Sales", "إجمالي المبيعات"),
            self.sales_value
        )

        # إنشاء بطاقة إجمالي المصروفات
        self.create_stat_card(
            self.stats_frame,
            self.t("Total Expenses", "إجمالي المصروفات"),
            self.expenses_value
        )

        # إنشاء بطاقة عدد فواتير البيع
        self.create_stat_card(
            self.stats_frame,
            self.t("Total Invoices", "إجمالي الفواتير"),
            self.invoices_value
        )

        # إنشاء زر تحديث التقارير لجلب أحدث البيانات من قاعدة البيانات
        ctk.CTkButton(
            self,
            text=self.t("Refresh Reports", "تحديث التقارير"),  # ترجمة نص الزر
            command=self.load_reports,  # تنفيذ دالة تحميل التقارير عند الضغط
            fg_color=self.colors["primary"],  # تحديد لون الزر الأساسي
            hover_color=self.colors["primary_hover"]  # تحديد لون الزر عند مرور المؤشر عليه
        ).pack(anchor="e", padx=20, pady=10)  # وضع الزر ناحية اليمين وإضافة مسافات

        # إنشاء عنوان جدول المنتجات الأكثر مبيعًا
        ctk.CTkLabel(
            self,
            text=self.t("Best Selling Products", "المنتجات الأكثر مبيعًا"),  # ترجمة العنوان
            font=("Arial", 18, "bold"),  # تحديد حجم الخط وجعله عريضًا
            text_color=self.colors["text"]  # استخدام لون النص الأساسي
        ).pack(anchor="w", padx=20, pady=(10, 5))  # وضع العنوان ناحية اليسار

        # إنشاء جدول يعرض أفضل 10 منتجات من حيث كمية المبيعات
        self.best_table = ttk.Treeview(
            self,
            columns=("name", "quantity", "total"),  # تحديد أسماء الأعمدة الداخلية
            show="headings",  # إخفاء العمود الافتراضي وعرض عناوين الأعمدة فقط
            height=5  # تحديد عدد الصفوف الظاهرة داخل الجدول
        )

        # تحديد أسماء الأعمدة التي تظهر للمستخدم حسب اللغة المختارة
        self.best_table.heading(
            "name", text=self.t("Product Name", "اسم المنتج")
        )

        self.best_table.heading(
            "quantity", text=self.t("Sold Quantity", "الكمية المباعة")
        )

        self.best_table.heading(
            "total", text=self.t("Total Sales", "إجمالي المبيعات")
        )

        # تحديد عرض كل عمود وطريقة محاذاة البيانات داخله
        self.best_table.column("name", width=250)  # توسيع عمود اسم المنتج
        self.best_table.column("quantity", width=150, anchor="center")  # توسيط الكمية
        self.best_table.column("total", width=180, anchor="center")  # توسيط إجمالي المبيعات

        # وضع جدول المنتجات الأكثر مبيعًا داخل الصفحة
        self.best_table.pack(fill="x", padx=20, pady=5)

        # إنشاء عنوان جدول المنتجات منخفضة المخزون
        ctk.CTkLabel(
            self,
            text=self.t("Low Stock Products", "المنتجات منخفضة المخزون"),  # ترجمة العنوان
            font=("Arial", 18, "bold"),  # تحديد حجم الخط وجعله عريضًا
            text_color=self.colors["text"]  # استخدام لون النص الأساسي
        ).pack(anchor="w", padx=20, pady=(15, 5))  # وضع العنوان وإضافة مسافات

        # إنشاء جدول يعرض المنتجات التي وصلت إلى الحد الأدنى للمخزون أو أقل
        self.low_table = ttk.Treeview(
            self,
            columns=("name", "quantity", "minimum"),  # تحديد الأعمدة الداخلية للجدول
            show="headings",  # عرض عناوين الأعمدة فقط
            height=5  # تحديد ارتفاع الجدول
        )

        # تحديد أسماء الأعمدة الظاهرة في جدول المخزون المنخفض
        self.low_table.heading(
            "name", text=self.t("Product Name", "اسم المنتج")
        )

        self.low_table.heading(
            "quantity", text=self.t("Current Quantity", "الكمية الحالية")
        )

        self.low_table.heading(
            "minimum", text=self.t("Minimum Quantity", "الحد الأدنى للكمية")
        )

        # تحديد عرض الأعمدة ومحاذاة البيانات
        self.low_table.column("name", width=250)  # توسيع عمود اسم المنتج
        self.low_table.column("quantity", width=150, anchor="center")  # توسيط الكمية الحالية
        self.low_table.column("minimum", width=180, anchor="center")  # توسيط الحد الأدنى

        # وضع الجدول في الصفحة والسماح له بالتمدد عند زيادة مساحة النافذة
        self.low_table.pack(
            fill="both", expand=True, padx=20, pady=(5, 15)
        )

    # دالة إنشاء بطاقة إحصائية لتجنب تكرار كود تصميم البطاقات
    def create_stat_card(self, parent, title, variable):

        # إنشاء إطار البطاقة باستخدام لون البطاقات الموحد في البرنامج
        card = ctk.CTkFrame(
            parent, fg_color=self.colors["card"]
        )
        card.pack(
            side="left",  # وضع البطاقة بجانب البطاقات الأخرى
            fill="both",  # السماح للبطاقة بالتمدد أفقيًا ورأسيًا
            expand=True,  # توزيع المساحة بالتساوي بين البطاقات
            padx=5  # إضافة مسافة بين البطاقات
        )

        # إنشاء عنوان البطاقة مثل إجمالي المبيعات أو إجمالي المصروفات
        ctk.CTkLabel(
            card,
            text=title,  # استقبال عنوان البطاقة من الدالة
            text_color=self.colors["secondary_text"],  # استخدام لون النص الثانوي
            font=("Arial", 14)  # تحديد حجم الخط
        ).pack(pady=(15, 5))  # إضافة مسافة أعلى وأسفل العنوان

        # إنشاء النص الذي يعرض الرقم داخل البطاقة
        ctk.CTkLabel(
            card,
            textvariable=variable,  # ربط النص بالمتغير الذي تتغير قيمته عند تحديث التقارير
            text_color=self.colors["text"],  # استخدام لون النص الأساسي
            font=("Arial", 23, "bold")  # تكبير الرقم وجعله عريضًا
        ).pack(pady=(5, 15))  # إضافة مسافة حول الرقم

    # دالة مساعدة لتنفيذ استعلامات القراءة من قاعدة البيانات
    def execute_query(self, query, values=()):

        connection = None  # تجهيز متغير الاتصال قبل محاولة فتح قاعدة البيانات
        cursor = None  # تجهيز متغير المؤشر قبل إنشائه

        try:
            connection = self.db.get_connection()  # فتح اتصال بقاعدة البيانات
            cursor = connection.cursor()  # إنشاء مؤشر لتنفيذ أوامر SQL
            cursor.execute(query, values)  # تنفيذ الاستعلام وإرسال القيم المطلوبة معه

            return cursor.fetchall()  # إرجاع جميع الصفوف الناتجة عن الاستعلام

        except Error as error:
            # عرض رسالة توضح وجود مشكلة أثناء الاتصال أو تنفيذ الاستعلام
            messagebox.showerror(
                self.raw_t("Database Error", "خطأ في قاعدة البيانات"),
                str(error)
            )
            return None  # إرجاع None حتى تعرف الدوال الأخرى أن الاستعلام فشل

        finally:
            # إغلاق المؤشر بعد الانتهاء حتى لا يظل مستهلكًا لموارد قاعدة البيانات
            if cursor:
                cursor.close()

            # التأكد من أن الاتصال ما زال مفتوحًا قبل إغلاقه
            if connection and connection.is_connected():
                connection.close()

    # دالة تحميل جميع بيانات التقارير وتحديث البطاقات والجداول
    def load_reports(self):

        # حساب إجمالي المبيعات خلال الشهر والسنة الحاليين
        # COALESCE تجعل النتيجة صفرًا بدلًا من NULL إذا لم توجد مبيعات
        sales = self.execute_query("""
            SELECT COALESCE(SUM(total), 0)
            FROM sales
            WHERE YEAR(sale_date) = YEAR(CURDATE())
            AND MONTH(sale_date) = MONTH(CURDATE())
        """)

        # حساب إجمالي المصروفات خلال الشهر والسنة الحاليين
        # يتم جمع قيمة amount من جدول المصروفات
        expenses = self.execute_query("""
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE YEAR(expense_date) = YEAR(CURDATE())
            AND MONTH(expense_date) = MONTH(CURDATE())
        """)

        # حساب عدد فواتير البيع المسجلة خلال الشهر الحالي
        # COUNT(*) يحسب عدد السجلات الموجودة في جدول المبيعات
        invoices = self.execute_query("""
            SELECT COUNT(*)
            FROM sales
            WHERE YEAR(sale_date) = YEAR(CURDATE())
            AND MONTH(sale_date) = MONTH(CURDATE())
        """)

        # التأكد من نجاح الاستعلامات الثلاثة قبل تحديث البطاقات
        # لو أي استعلام رجع None فهذا معناه أن هناك خطأ في قاعدة البيانات
        if sales is None or expenses is None or invoices is None:
            return  # إيقاف الدالة دون تحديث بيانات غير مكتملة

        # تحويل إجمالي المبيعات إلى رقم عشري وعرضه بفاصلتين بعد العلامة العشرية
        # {:,.2f} تجعل الرقم منسقًا بفواصل الآلاف ورقمين عشريين
        self.sales_value.set(
            f"{float(sales[0][0]):,.2f}"
        )

        # تحديث بطاقة إجمالي المصروفات بنفس طريقة تنسيق المبيعات
        self.expenses_value.set(
            f"{float(expenses[0][0]):,.2f}"
        )

        # تحديث بطاقة عدد الفواتير وتحويل الرقم إلى نص لعرضه
        self.invoices_value.set(
            str(invoices[0][0])
        )

        # تحميل المنتجات الأكثر مبيعًا وعرضها في الجدول الأول
        self.load_best_selling()

        # تحميل المنتجات التي وصلت إلى الحد الأدنى للمخزون أو أقل
        self.load_low_stock()

    # دالة تحميل المنتجات الأكثر مبيعًا
    def load_best_selling(self):

        # تجميع كميات المبيعات لكل منتج وترتيب المنتجات من الأعلى للأقل
        # SUM(si.quantity) تحسب إجمالي الكمية المباعة من المنتج
        # SUM(si.item_total) تحسب إجمالي قيمة مبيعات المنتج
        # JOIN يربط تفاصيل الفواتير بجدول المنتجات
        # LIMIT 10 يعرض أفضل عشرة منتجات فقط
        rows = self.execute_query("""
            SELECT p.product_name, SUM(si.quantity),
                   SUM(si.item_total)
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            GROUP BY p.product_id, p.product_name
            ORDER BY SUM(si.quantity) DESC
            LIMIT 10
        """)

        # إيقاف الدالة إذا حدث خطأ أثناء جلب البيانات
        if rows is None:
            return

        # حذف البيانات القديمة من الجدول قبل عرض النتائج الجديدة
        self.best_table.delete(
            *self.best_table.get_children()
        )

        # المرور على كل منتج وإضافة بياناته إلى الجدول
        for row in rows:

            # إضافة اسم المنتج والكمية المباعة وإجمالي المبيعات
            # تنسيق إجمالي المبيعات ليظهر بفواصل الآلاف ورقمين عشريين
            self.best_table.insert(
                "", "end",
                values=(
                    row[0],
                    row[1],
                    f"{float(row[2]):,.2f}"
                )
            )

    # دالة تحميل المنتجات منخفضة المخزون
    def load_low_stock(self):

        # جلب اسم المنتج والكمية الحالية والحد الأدنى المسموح به
        # الشرط quantity <= min_quantity يعرض المنتجات التي وصلت للحد الأدنى أو أقل
        # ORDER BY quantity ASC يرتب المنتجات من الأقل كمية إلى الأعلى
        rows = self.execute_query("""
            SELECT product_name, quantity, min_quantity
            FROM products
            WHERE quantity <= min_quantity
            ORDER BY quantity ASC
        """)

        # إيقاف الدالة إذا حدث خطأ أثناء جلب البيانات
        if rows is None:
            return

        # حذف البيانات القديمة من الجدول قبل عرض المنتجات المحدثة
        self.low_table.delete(
            *self.low_table.get_children()
        )

        # المرور على المنتجات منخفضة المخزون وإضافتها إلى الجدول
        for row in rows:

            # عرض اسم المنتج والكمية الحالية والحد الأدنى للمخزون
            self.low_table.insert(
                "", "end",
                values=row
            )