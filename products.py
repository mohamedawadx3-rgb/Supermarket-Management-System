# ============================================================
# مشروع Supermarket Management System
# الملف: products.py
# الوظيفة: إدارة المنتجات (إضافة وتعديل وحذف وبحث)
# ============================================================

import customtkinter as ctk
from tkinter import ttk, messagebox


class ProductsPage(ctk.CTkFrame):

    # ========================================================
    # إنشاء الصفحة
    # ========================================================

    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color="transparent")

        self.db = db
        self.app = app
        self.colors = app.colors
        self.entries = {}

        self.create_interface()
        self.load_products()

    # ========================================================
    # دالة الترجمة
    # ========================================================

    def t(self, english, arabic):
        return self.app.t(english, arabic)

    # ترجمة رسائل النوافذ المنبثقة بدون معالجة RTL
    def raw_t(self, english, arabic):
        return self.app.raw_t(english, arabic)

    # ========================================================
    # معالجة اتجاه النص العربي
    # ========================================================

    def clean_rtl(self, value):
        return str(value).replace(
            "\u200f", ""
        ).replace(
            "\u200e", ""
        ).strip()

    def rtl_focus_in(self, event):
        entry = event.widget
        value = entry.get()

        if not value.startswith("\u200f"):
            entry.insert(0, "\u200f")

        entry.icursor("end")

    def rtl_focus_out(self, event):
        entry = event.widget
        value = self.clean_rtl(entry.get())

        entry.delete(0, "end")
        entry.insert(0, value)

    # ========================================================
    # إنشاء الواجهة
    # ========================================================

    def create_interface(self):

        # عنوان الصفحة
        ctk.CTkLabel(
            self,
            text=self.t("Products Management", "إدارة المنتجات"),
            font=("Arial", 24, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=(5, 15))

        # إطار بيانات المنتج
        form = ctk.CTkFrame(
            self,
            fg_color=self.colors["card"]
        )
        form.pack(fill="x", pady=5)

        # الحقول
        fields = [
            ("name", "Product Name", "اسم المنتج"),
            ("barcode", "Barcode", "الباركود"),
            ("buy", "Purchase Price", "سعر الشراء"),
            ("sell", "Selling Price", "سعر البيع"),
            ("quantity", "Quantity", "الكمية"),
            ("minimum", "Minimum Quantity", "الحد الأدنى"),
            ("expiry", "Expiry Date YYYY-MM-DD", "تاريخ الصلاحية YYYY-MM-DD")
        ]

        # إنشاء خانات الإدخال
        for i, (key, english, arabic) in enumerate(fields):

            row, col = divmod(i, 4)

            direction = "right" if key == "name" else "left"

            entry = ctk.CTkEntry(
                form,
                placeholder_text=self.t(english, arabic),
                justify=direction
            )

            entry.grid(
                row=row,
                column=col,
                padx=8,
                pady=10,
                sticky="ew"
            )

            self.entries[key] = entry

            if key == "name":
                entry.bind("<FocusIn>", self.rtl_focus_in)
                entry.bind("<FocusOut>", self.rtl_focus_out)

        # توزيع الأعمدة
        for col in range(4):
            form.grid_columnconfigure(col, weight=1)

        # إطار الأزرار
        buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        buttons.pack(fill="x", pady=10)

        actions = [
            ("Add Product", "إضافة منتج", self.add_product),
            ("Update", "تعديل", self.update_product),
            ("Delete", "حذف", self.delete_product),
            ("Clear", "مسح", self.clear_fields)
        ]

        for english, arabic, command in actions:
            ctk.CTkButton(
                buttons,
                text=self.t(english, arabic),
                command=command,
                width=115
            ).pack(side="left", padx=5)

        # إطار البحث
        search_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        search_frame.pack(fill="x", pady=8)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self.t(
                "Search by product name or barcode",
                "ابحث باسم المنتج أو الباركود"
            ),
            justify="right"
        )

        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        self.search_entry.bind("<FocusIn>", self.rtl_focus_in)
        self.search_entry.bind("<FocusOut>", self.rtl_focus_out)

        # زر البحث
        ctk.CTkButton(
            search_frame,
            text=self.t("Search", "بحث"),
            command=self.search_products,
            width=100
        ).pack(side="left", padx=5)

        # عرض جميع المنتجات
        ctk.CTkButton(
            search_frame,
            text=self.t("Show All", "عرض الكل"),
            command=self.load_products,
            width=100
        ).pack(side="left", padx=5)

        # إطار الجدول
        table_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["card"]
        )
        table_frame.pack(
            fill="both",
            expand=True,
            pady=10
        )

        # أعمدة الجدول
        columns = (
            "id", "name", "barcode", "buy",
            "sell", "quantity", "minimum", "expiry"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        # أسماء الأعمدة باللغتين
        headings = {
            "id": ("ID", "رقم"),
            "name": ("Product Name", "اسم المنتج"),
            "barcode": ("Barcode", "الباركود"),
            "buy": ("Purchase Price", "سعر الشراء"),
            "sell": ("Selling Price", "سعر البيع"),
            "quantity": ("Quantity", "الكمية"),
            "minimum": ("Minimum", "الحد الأدنى"),
            "expiry": ("Expiry Date", "تاريخ الصلاحية")
        }

        # ضبط عناوين وأحجام الأعمدة
        for col, (english, arabic) in headings.items():

            self.tree.heading(
                col,
                text=self.t(english, arabic)
            )

            self.tree.column(
                col,
                width=110,
                anchor="center",
                stretch=False
            )

        # ضبط عمود اسم المنتج
        self.tree.column(
            "name",
            width=160,
            anchor="e",
            stretch=False
        )

        self.tree.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_product
        )

    # ========================================================
    # تنفيذ أوامر قاعدة البيانات
    # ========================================================

    def execute_query(self, query, values=(), fetch=False):

        connection = None
        cursor = None

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()

            cursor.execute(query, values)

            result = cursor.fetchall() if fetch else None

            if not fetch:
                connection.commit()

            return result if fetch else True

        except Exception as error:

            messagebox.showerror(
                self.raw_t("Database Error", "خطأ في قاعدة البيانات"),
                str(error)
            )

            return None if fetch else False

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # ========================================================
    # قراءة بيانات المنتج والتحقق منها
    # ========================================================

    def get_form_data(self):

        data = {
            key: self.clean_rtl(entry.get())
            for key, entry in self.entries.items()
        }

        # التحقق من اسم المنتج
        if not data["name"]:

            messagebox.showwarning(
                self.raw_t("Warning", "تحذير"),
                self.t(
                    "Enter product name.",
                    "من فضلك أدخل اسم المنتج."
                )
            )
            return None

        try:
            data["buy"] = float(data["buy"])
            data["sell"] = float(data["sell"])
            data["quantity"] = int(data["quantity"])
            data["minimum"] = int(data["minimum"])

            # منع القيم السالبة
            if min(
                data["buy"],
                data["sell"],
                data["quantity"],
                data["minimum"]
            ) < 0:
                raise ValueError

        except ValueError:

            messagebox.showwarning(
                self.raw_t("Warning", "تحذير"),
                self.t(
                    "Enter valid prices and quantities.",
                    "أدخل أسعار وكميات صحيحة."
                )
            )
            return None

        return data

    # ========================================================
    # إضافة منتج جديد
    # ========================================================

    def add_product(self):

        data = self.get_form_data()

        if not data:
            return

        query = """
            INSERT INTO products
            (product_name, barcode, purchase_price, selling_price,
             quantity, min_quantity, expiry_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data["name"],
            data["barcode"] or None,
            data["buy"],
            data["sell"],
            data["quantity"],
            data["minimum"],
            data["expiry"] or None
        )

        if self.execute_query(query, values):

            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.t(
                    "Product added successfully.",
                    "تمت إضافة المنتج بنجاح."
                )
            )

            self.clear_fields()
            self.load_products()

    # ========================================================
    # تحديد المنتج المختار
    # ========================================================

    def select_product(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(
            selected[0],
            "values"
        )

        keys = [
            "name", "barcode", "buy", "sell",
            "quantity", "minimum", "expiry"
        ]

        for key, value in zip(keys, values[1:]):

            value = self.clean_rtl(value)

            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, str(value))

    # ========================================================
    # تعديل بيانات المنتج
    # ========================================================

    def update_product(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(
                self.raw_t("Warning", "تحذير"),
                self.t(
                    "Select a product first.",
                    "اختر منتجاً أولاً."
                )
            )
            return

        data = self.get_form_data()

        if not data:
            return

        product_id = self.tree.item(
            selected[0],
            "values"
        )[0]

        query = """
            UPDATE products SET
            product_name=%s,
            barcode=%s,
            purchase_price=%s,
            selling_price=%s,
            quantity=%s,
            min_quantity=%s,
            expiry_date=%s
            WHERE product_id=%s
        """

        values = (
            data["name"],
            data["barcode"] or None,
            data["buy"],
            data["sell"],
            data["quantity"],
            data["minimum"],
            data["expiry"] or None,
            product_id
        )

        if self.execute_query(query, values):

            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.t(
                    "Product updated.",
                    "تم تعديل بيانات المنتج."
                )
            )

            self.clear_fields()
            self.load_products()

    # ========================================================
    # حذف منتج
    # ========================================================

    def delete_product(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(
                self.raw_t("Warning", "تحذير"),
                self.t(
                    "Select a product first.",
                    "اختر منتجاً أولاً."
                )
            )
            return

        product_id = self.tree.item(
            selected[0],
            "values"
        )[0]

        confirm = messagebox.askyesno(
            self.raw_t("Confirm", "تأكيد"),
            self.t(
                "Delete this product?",
                "هل أنت متأكد من حذف هذا المنتج؟"
            )
        )

        if confirm:

            if self.execute_query(
                "DELETE FROM products WHERE product_id=%s",
                (product_id,)
            ):

                messagebox.showinfo(
                    self.raw_t("Success", "نجاح"),
                    self.t(
                        "Product deleted successfully.",
                        "تم حذف المنتج بنجاح."
                    )
                )

                self.clear_fields()
                self.load_products()

    # ========================================================
    # عرض جميع المنتجات
    # ========================================================

    def load_products(self):

        rows = self.execute_query(
            """
            SELECT product_id, product_name, barcode,
            purchase_price, selling_price, quantity,
            min_quantity, expiry_date
            FROM products
            ORDER BY product_id DESC
            """,
            fetch=True
        )

        if rows is not None:
            self.display_products(rows)

    # ========================================================
    # البحث عن منتج
    # ========================================================

    def search_products(self):

        keyword = self.clean_rtl(
            self.search_entry.get()
        )

        rows = self.execute_query(
            """
            SELECT product_id, product_name, barcode,
            purchase_price, selling_price, quantity,
            min_quantity, expiry_date
            FROM products
            WHERE product_name LIKE %s OR barcode LIKE %s
            ORDER BY product_id DESC
            """,
            (f"%{keyword}%", f"%{keyword}%"),
            fetch=True
        )

        if rows is not None:
            self.display_products(rows)

    # ========================================================
    # تحديث بيانات الجدول
    # ========================================================

    def display_products(self, rows):

        self.tree.delete(
            *self.tree.get_children()
        )

        for row in rows:

            values = list(row)

            # إضافة علامة اتجاه RTL للعرض فقط
            if values[1]:
                values[1] = "\u200f" + str(values[1])

            self.tree.insert(
                "",
                "end",
                values=values
            )

    # ========================================================
    # تفريغ خانات الإدخال
    # ========================================================

    def clear_fields(self):

        for entry in self.entries.values():
            entry.delete(0, "end")

        self.tree.selection_remove(
            self.tree.selection()
        )