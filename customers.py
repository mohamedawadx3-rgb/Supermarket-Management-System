# ============================================================
# إدارة العملاء
# الملف: customers.py
# الوظيفة: إضافة وتعديل وحذف والبحث عن العملاء
# ============================================================

import customtkinter as ctk
from tkinter import ttk, messagebox


class CustomersPage(ctk.CTkFrame):

    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color="transparent")

        self.db = db
        self.app = app
        self.colors = app.colors
        self.selected_id = None

        self.create_interface()
        self.load_customers()

    # ترجمة نصوص الواجهة مع معالجة اتجاه العربي
    def t(self, english, arabic):
        return self.app.t(english, arabic)

    # ترجمة الرسائل المنبثقة بدون معالجة اتجاه النص
    def raw_t(self, english, arabic):
        return self.app.raw_t(english, arabic)

    # إنشاء الواجهة
    def create_interface(self):

        ctk.CTkLabel(
            self,
            text=self.t("Customers Management", "إدارة العملاء"),
            font=("Arial", 24, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=15)

        # نموذج بيانات العميل
        form = ctk.CTkFrame(
            self,
            fg_color=self.colors["card"]
        )
        form.pack(fill="x", pady=10)

        self.name_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Customer Name", "اسم العميل"),
            width=190
        )
        self.name_entry.pack(side="left", padx=5, pady=15)

        self.phone_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Phone", "رقم الهاتف"),
            width=150
        )
        self.phone_entry.pack(side="left", padx=5, pady=15)

        self.address_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Address", "العنوان"),
            width=190
        )
        self.address_entry.pack(side="left", padx=5, pady=15)

        # أزرار التحكم
        buttons = [
            (self.t("Add", "إضافة"), self.add_customer),
            (self.t("Update", "تعديل"), self.update_customer),
            (self.t("Delete", "حذف"), self.delete_customer),
            (self.t("Clear", "مسح"), self.clear_fields)
        ]

        for title, command in buttons:
            ctk.CTkButton(
                form,
                text=title,
                command=command,
                width=100
            ).pack(side="left", padx=4)

        # البحث
        search_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        search_frame.pack(fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self.t(
                "Search by name or phone...",
                "ابحث بالاسم أو رقم الهاتف..."
            )
        )
        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        ctk.CTkButton(
            search_frame,
            text=self.t("Search", "بحث"),
            command=self.search_customers,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text=self.t("Show All", "عرض الكل"),
            command=self.load_customers,
            width=100
        ).pack(side="left", padx=5)

        # جدول العملاء
        self.tree = ttk.Treeview(
            self,
            columns=("id", "name", "phone", "address"),
            show="headings"
        )

        columns = [
            ("id", self.t("ID", "المعرف"), 60),
            ("name", self.t("Customer Name", "اسم العميل"), 220),
            ("phone", self.t("Phone", "رقم الهاتف"), 160),
            ("address", self.t("Address", "العنوان"), 300)
        ]

        for col, title, width in columns:
            self.tree.heading(col, text=title)
            self.tree.column(
                col,
                width=width,
                anchor="center"
            )

        self.tree.pack(
            fill="both",
            expand=True,
            pady=10
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_customer
        )

    # تنفيذ أوامر قاعدة البيانات
    def execute_query(self, query, values=(), fetch=False):
        connection = cursor = None

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

    # إضافة عميل
    def add_customer(self):

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Enter customer name.",
                    "من فضلك أدخل اسم العميل."
                )
            )
            return

        success = self.execute_query(
            """INSERT INTO customers
               (customer_name, phone, address)
               VALUES (%s, %s, %s)""",
            (name, phone, address)
        )

        if success:
            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.raw_t(
                    "Customer added successfully.",
                    "تمت إضافة العميل بنجاح."
                )
            )
            self.clear_fields()
            self.load_customers()

    # اختيار عميل من الجدول
    def select_customer(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        self.selected_id = values[0]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, values[1])

        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, values[2])

        self.address_entry.delete(0, "end")
        self.address_entry.insert(0, values[3])

    # تعديل بيانات عميل
    def update_customer(self):

        if not self.selected_id:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Select a customer first.",
                    "من فضلك اختر عميلًا أولًا."
                )
            )
            return

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Enter customer name.",
                    "من فضلك أدخل اسم العميل."
                )
            )
            return

        success = self.execute_query(
            """UPDATE customers
               SET customer_name=%s, phone=%s, address=%s
               WHERE customer_id=%s""",
            (name, phone, address, self.selected_id)
        )

        if success:
            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.raw_t(
                    "Customer updated successfully.",
                    "تم تعديل بيانات العميل بنجاح."
                )
            )
            self.clear_fields()
            self.load_customers()

    # حذف عميل
    def delete_customer(self):

        if not self.selected_id:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Select a customer first.",
                    "من فضلك اختر عميلًا أولًا."
                )
            )
            return

        confirm = messagebox.askyesno(
            self.raw_t("Confirm", "تأكيد"),
            self.raw_t(
                "Delete this customer?",
                "هل أنت متأكد من حذف هذا العميل؟"
            )
        )

        if confirm:
            success = self.execute_query(
                "DELETE FROM customers WHERE customer_id=%s",
                (self.selected_id,)
            )

            if success:
                messagebox.showinfo(
                    self.raw_t("Success", "نجاح"),
                    self.raw_t(
                        "Customer deleted successfully.",
                        "تم حذف العميل بنجاح."
                    )
                )
                self.clear_fields()
                self.load_customers()

    # تحميل جميع العملاء
    def load_customers(self):

        rows = self.execute_query(
            """SELECT customer_id, customer_name, phone, address
               FROM customers
               ORDER BY customer_id DESC""",
            fetch=True
        )

        if rows is not None:
            self.display_customers(rows)

    # البحث بالاسم أو رقم الهاتف
    def search_customers(self):

        keyword = self.search_entry.get().strip()

        rows = self.execute_query(
            """SELECT customer_id, customer_name, phone, address
               FROM customers
               WHERE customer_name LIKE %s OR phone LIKE %s
               ORDER BY customer_id DESC""",
            (f"%{keyword}%", f"%{keyword}%"),
            fetch=True
        )

        if rows is not None:
            self.display_customers(rows)

    # عرض العملاء في الجدول
    def display_customers(self, rows):

        self.tree.delete(*self.tree.get_children())

        for row in rows:
            self.tree.insert("", "end", values=row)

    # تفريغ الحقول
    def clear_fields(self):

        self.name_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.address_entry.delete(0, "end")

        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())