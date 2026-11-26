import customtkinter as ctk
from tkinter import ttk, messagebox
from mysql.connector import Error


class InventoryPage(ctk.CTkFrame):

    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color="transparent")

        self.db = db
        self.app = app
        self.colors = app.colors
        self.selected_product_id = None

        self.create_interface()
        self.load_inventory()
        self.load_movements()

    # دالة مختصرة لترجمة النصوص
    def t(self, english, arabic=None):
        return self.app.t(english, arabic)

    # ترجمة النصوص بدون معالجة اتجاه العربية
    def raw_t(self, english, arabic):
        return self.app.raw_t(english, arabic)

    def create_interface(self):

        ctk.CTkLabel(
            self,
            text=self.t("Inventory Management", "إدارة المخزون"),
            font=("Arial", 25, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", padx=20, pady=(15, 3))

        ctk.CTkLabel(
            self,
            text=self.t(
                "Monitor stock and manage inventory movements",
                "متابعة المخزون وإدارة حركات المنتجات"
            ),
            text_color=self.colors["secondary_text"]
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # البحث عن المنتجات
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text=self.t(
                "Search product...", "ابحث عن منتج..."
            ),
            width=300,
            height=35
        )
        self.search_entry.pack(anchor="w", padx=20, pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_inventory)

        # جدول المنتجات
        columns = ("id", "name", "quantity", "minimum", "status")

        self.products_table = ttk.Treeview(
            self, columns=columns, show="headings", height=8
        )

        headings = {
            "id": self.t("ID", "الرقم"),
            "name": self.t("Product Name", "اسم المنتج"),
            "quantity": self.t("Current Stock", "الكمية الحالية"),
            "minimum": self.t("Minimum Stock", "الحد الأدنى"),
            "status": self.t("Status", "الحالة")
        }

        for column, heading in headings.items():
            self.products_table.heading(column, text=heading)
            self.products_table.column(
                column, width=140, anchor="center"
            )

        self.products_table.column("name", width=220)
        self.products_table.pack(fill="x", padx=20, pady=10)

        self.products_table.bind(
            "<<TreeviewSelect>>", self.select_product
        )

        # إطار تسجيل حركة المخزون
        movement_frame = ctk.CTkFrame(
            self, fg_color=self.colors["card"]
        )
        movement_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            movement_frame,
            text=self.t("Stock Movement", "حركة المخزون"),
            font=("Arial", 17, "bold")
        ).pack(anchor="w", padx=15, pady=10)

        self.selected_label = ctk.CTkLabel(
            movement_frame,
            text=self.t("Selected Product: None", "المنتج المحدد: لا يوجد")
        )
        self.selected_label.pack(anchor="w", padx=15, pady=5)

        fields = ctk.CTkFrame(
            movement_frame, fg_color="transparent"
        )
        fields.pack(fill="x", padx=15, pady=5)

        self.quantity_entry = ctk.CTkEntry(
            fields,
            placeholder_text=self.t("Quantity", "الكمية"),
            width=150
        )
        self.quantity_entry.pack(side="left", padx=5)

        # قيم IN و OUT تظل كما هي لتوافق قاعدة البيانات
        self.movement_type = ctk.CTkOptionMenu(
            fields,
            values=["IN", "OUT"],
            width=130
        )
        self.movement_type.pack(side="left", padx=5)

        self.notes_entry = ctk.CTkEntry(
            fields,
            placeholder_text=self.t(
                "Notes (optional)", "ملاحظات (اختياري)"
            ),
            width=220
        )
        self.notes_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            fields,
            text=self.t("Save Movement", "حفظ الحركة"),
            command=self.save_movement,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"]
        ).pack(side="left", padx=5)

        # جدول سجل الحركات
        ctk.CTkLabel(
            self,
            text=self.t(
                "Recent Stock Movements", "أحدث حركات المخزون"
            ),
            font=("Arial", 18, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", padx=20, pady=(10, 5))

        history_columns = (
            "id", "product", "type", "quantity", "notes", "date"
        )

        self.history_table = ttk.Treeview(
            self,
            columns=history_columns,
            show="headings",
            height=7
        )

        history_headings = {
            "id": self.t("ID", "الرقم"),
            "product": self.t("Product", "المنتج"),
            "type": self.t("Movement", "نوع الحركة"),
            "quantity": self.t("Quantity", "الكمية"),
            "notes": self.t("Notes", "ملاحظات"),
            "date": self.t("Date", "التاريخ")
        }

        for column, heading in history_headings.items():
            self.history_table.heading(column, text=heading)
            self.history_table.column(
                column, width=110, anchor="center"
            )

        self.history_table.column("product", width=170)
        self.history_table.column("notes", width=180)

        self.history_table.pack(
            fill="both", expand=True, padx=20, pady=(5, 15)
        )

    # تنفيذ استعلامات قاعدة البيانات
    def execute_query(self, query, values=(), fetch=False):

        connection = None
        cursor = None

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, values)

            if fetch:
                return cursor.fetchall()

            connection.commit()
            return True

        except Error as error:
            messagebox.showerror(
                self.raw_t("Database Error", "خطأ في قاعدة البيانات"),
                str(error)
            )
            return None

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # تحميل المنتجات
    def load_inventory(self, search=""):

        query = """
            SELECT product_id, product_name, quantity, min_quantity
            FROM products
            WHERE product_name LIKE %s OR barcode LIKE %s
            ORDER BY product_id DESC
        """

        value = f"%{search}%"
        rows = self.execute_query(
            query, (value, value), fetch=True
        )

        if rows is None:
            return

        self.products_table.delete(
            *self.products_table.get_children()
        )

        for row in rows:
            product_id, name, quantity, minimum = row

            status = (
                self.t("Low Stock", "مخزون منخفض")
                if quantity <= minimum
                else self.t("Available", "متوفر")
            )

            self.products_table.insert(
                "", "end",
                values=(product_id, name, quantity, minimum, status)
            )

    # البحث عن منتج
    def search_inventory(self, event=None):

        search = self.search_entry.get().strip()
        self.load_inventory(search)

    # تحديد المنتج من الجدول
    def select_product(self, event=None):

        selected = self.products_table.selection()

        if not selected:
            return

        values = self.products_table.item(
            selected[0], "values"
        )

        self.selected_product_id = int(values[0])

        self.selected_label.configure(
            text=f"{self.t('Selected Product', 'المنتج المحدد')}: {values[1]}"
        )

    # تحميل سجل آخر 20 حركة
    def load_movements(self):

        query = """
            SELECT m.movement_id, p.product_name, m.movement_type,
                   m.quantity, m.notes, m.movement_date
            FROM inventory_movements m
            JOIN products p ON m.product_id = p.product_id
            ORDER BY m.movement_id DESC
            LIMIT 20
        """

        rows = self.execute_query(query, fetch=True)

        if rows is None:
            return

        self.history_table.delete(
            *self.history_table.get_children()
        )

        for row in rows:
            self.history_table.insert(
                "", "end", values=row
            )

    # تسجيل حركة جديدة
    def save_movement(self):

        if self.selected_product_id is None:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Please select a product first.",
                    "من فضلك اختر منتجًا أولًا."
                )
            )
            return

        try:
            amount = int(self.quantity_entry.get())

            if amount <= 0:
                raise ValueError(
                    self.t(
                        "Quantity must be greater than zero.",
                        "يجب أن تكون الكمية أكبر من صفر."
                    )
                )

        except ValueError as error:
            messagebox.showwarning(
                self.raw_t("Invalid Quantity", "كمية غير صحيحة"),
                str(error)
            )
            return

        movement = self.movement_type.get()
        notes = self.notes_entry.get().strip()

        connection = None
        cursor = None

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()

            # بدء معاملة لحماية بيانات المخزون
            connection.start_transaction()

            cursor.execute(
                """
                SELECT quantity FROM products
                WHERE product_id=%s FOR UPDATE
                """,
                (self.selected_product_id,)
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError(
                    self.t(
                        "Product was not found.",
                        "المنتج غير موجود."
                    )
                )

            current_quantity = int(result[0])

            if movement == "OUT" and amount > current_quantity:
                raise ValueError(
                    self.t(
                        "Not enough stock available.",
                        "الكمية الموجودة في المخزون غير كافية."
                    )
                )

            # حساب الكمية الجديدة
            if movement == "IN":
                new_quantity = current_quantity + amount
            else:
                new_quantity = current_quantity - amount

            # تحديث كمية المنتج
            cursor.execute(
                """
                UPDATE products SET quantity=%s
                WHERE product_id=%s
                """,
                (new_quantity, self.selected_product_id)
            )

            # تسجيل الحركة في سجل المخزون
            cursor.execute(
                """
                INSERT INTO inventory_movements
                (product_id, movement_type, quantity, notes)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    self.selected_product_id,
                    movement,
                    amount,
                    notes
                )
            )

            connection.commit()

            messagebox.showinfo(
                self.raw_t("Success", "تم بنجاح"),
                self.t(
                    "Stock movement saved successfully.",
                    "تم تسجيل حركة المخزون بنجاح."
                )
            )

            # تفريغ الحقول بعد نجاح التسجيل
            self.quantity_entry.delete(0, "end")
            self.notes_entry.delete(0, "end")

            self.load_inventory(
                self.search_entry.get().strip()
            )
            self.load_movements()

        except (Error, ValueError) as error:

            if connection:
                connection.rollback()

            messagebox.showerror(
                self.raw_t("Movement Error", "خطأ في حركة المخزون"),
                str(error)
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()