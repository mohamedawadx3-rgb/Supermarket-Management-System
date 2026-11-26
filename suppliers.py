# إدارة الموردين في السوبر ماركت

import customtkinter as ctk
from tkinter import messagebox, ttk


class SuppliersPage(ctk.CTkFrame):

    def __init__(self, parent, db, app):
        super().__init__(parent)

        self.db = db
        self.app = app
        self.colors = app.colors
        self.selected_id = None

        self.create_interface()
        self.load_suppliers()

    # ترجمة النصوص
    def t(self, english, arabic):
        return self.app.t(english, arabic)

    # ترجمة النصوص بدون معالجة اتجاه العربية
    def raw_t(self, english, arabic):
        return self.app.raw_t(english, arabic)

    # إنشاء الواجهة
    def create_interface(self):

        ctk.CTkLabel(
            self,
            text=self.t("Suppliers Management", "إدارة الموردين"),
            font=("Arial", 24, "bold"),
            text_color=self.colors["text"]
        ).pack(pady=15)

        # إطار بيانات المورد
        form = ctk.CTkFrame(
            self,
            fg_color=self.colors["card"]
        )
        form.pack(fill="x", padx=20, pady=10)

        # خانات الإدخال
        self.name_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Supplier Name", "اسم المورد"),
            width=250
        )
        self.name_entry.pack(side="left", padx=10, pady=15)

        self.phone_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Phone", "رقم الهاتف"),
            width=200
        )
        self.phone_entry.pack(side="left", padx=10, pady=15)

        self.address_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Address", "العنوان"),
            width=250
        )
        self.address_entry.pack(side="left", padx=10, pady=15)

        # أزرار التحكم
        buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        buttons.pack(fill="x", padx=20, pady=5)

        actions = [
            (self.t("Add", "إضافة"), self.add_supplier),
            (self.t("Update", "تعديل"), self.update_supplier),
            (self.t("Delete", "حذف"), self.delete_supplier),
            (self.t("Clear", "مسح"), self.clear_fields)
        ]

        for title, command in actions:
            ctk.CTkButton(
                buttons,
                text=title,
                command=command,
                width=110
            ).pack(side="left", padx=5, pady=8)

        # خانة البحث
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text=self.t(
                "Search by name or phone...",
                "ابحث بالاسم أو رقم الهاتف..."
            )
        )
        self.search_entry.pack(fill="x", padx=20, pady=10)

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.search_suppliers()
        )

        # إطار الجدول
        table_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["card"]
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # أعمدة الجدول
        columns = ("id", "name", "phone", "address")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": self.t("ID", "المعرف"),
            "name": self.t("Supplier Name", "اسم المورد"),
            "phone": self.t("Phone", "رقم الهاتف"),
            "address": self.t("Address", "العنوان")
        }

        for col, heading in headings.items():
            self.table.heading(col, text=heading)

        # ضبط عرض الأعمدة
        self.table.column(
            "id", width=80, minwidth=80,
            anchor="center", stretch=False
        )

        self.table.column(
            "name", width=220, minwidth=180,
            anchor="center", stretch=True
        )

        self.table.column(
            "phone", width=160, minwidth=130,
            anchor="center", stretch=False
        )

        self.table.column(
            "address", width=280, minwidth=200,
            anchor="center", stretch=True
        )

        self.table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.table.bind(
            "<<TreeviewSelect>>",
            self.select_supplier
        )

    # تنفيذ أوامر قاعدة البيانات
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

        except Exception as error:
            messagebox.showerror(
                self.raw_t("Database Error", "خطأ في قاعدة البيانات"),
                str(error)
            )
            return False

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # إضافة مورد
    def add_supplier(self):

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Supplier name is required.",
                    "اسم المورد مطلوب."
                )
            )
            return

        query = """
            INSERT INTO suppliers
            (supplier_name, phone, address)
            VALUES (%s, %s, %s)
        """

        if self.execute_query(query, (name, phone, address)):
            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.t(
                    "Supplier added successfully.",
                    "تمت إضافة المورد بنجاح."
                )
            )
            self.clear_fields()
            self.load_suppliers()

    # تعديل مورد
    def update_supplier(self):

        if self.selected_id is None:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Select a supplier first.",
                    "من فضلك اختر موردًا أولًا."
                )
            )
            return

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Supplier name is required.",
                    "اسم المورد مطلوب."
                )
            )
            return

        query = """
            UPDATE suppliers
            SET supplier_name=%s, phone=%s, address=%s
            WHERE supplier_id=%s
        """

        values = (name, phone, address, self.selected_id)

        if self.execute_query(query, values):
            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.t(
                    "Supplier updated successfully.",
                    "تم تعديل بيانات المورد بنجاح."
                )
            )
            self.clear_fields()
            self.load_suppliers()

    # حذف مورد
    def delete_supplier(self):

        if self.selected_id is None:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Select a supplier first.",
                    "من فضلك اختر موردًا أولًا."
                )
            )
            return

        confirm = messagebox.askyesno(
            self.raw_t("Confirm Delete", "تأكيد الحذف"),
            self.t(
                "Are you sure you want to delete this supplier?",
                "هل أنت متأكد من حذف هذا المورد؟"
            )
        )

        if not confirm:
            return

        query = "DELETE FROM suppliers WHERE supplier_id=%s"

        if self.execute_query(query, (self.selected_id,)):
            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.t(
                    "Supplier deleted successfully.",
                    "تم حذف المورد بنجاح."
                )
            )
            self.clear_fields()
            self.load_suppliers()

    # تحميل الموردين
    def load_suppliers(self):

        query = """
            SELECT supplier_id, supplier_name, phone, address
            FROM suppliers
            ORDER BY supplier_id DESC
        """

        rows = self.execute_query(query, fetch=True)

        if rows is not None:
            self.display_suppliers(rows)

    # البحث عن الموردين
    def search_suppliers(self):

        keyword = self.search_entry.get().strip()

        query = """
            SELECT supplier_id, supplier_name, phone, address
            FROM suppliers
            WHERE supplier_name LIKE %s OR phone LIKE %s
            ORDER BY supplier_id DESC
        """

        value = f"%{keyword}%"

        rows = self.execute_query(
            query, (value, value), fetch=True
        )

        if rows is not None:
            self.display_suppliers(rows)

    # عرض الموردين في الجدول
    def display_suppliers(self, rows):

        for item in self.table.get_children():
            self.table.delete(item)

        for row in rows:
            self.table.insert("", "end", values=row)

    # اختيار مورد
    def select_supplier(self, event=None):

        selected = self.table.selection()

        if not selected:
            return

        data = self.table.item(selected[0], "values")

        self.selected_id = data[0]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, data[1])

        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, data[2] or "")

        self.address_entry.delete(0, "end")
        self.address_entry.insert(0, data[3] or "")

    # تفريغ الخانات
    def clear_fields(self):

        self.name_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.address_entry.delete(0, "end")

        self.selected_id = None

        for item in self.table.selection():
            self.table.selection_remove(item)