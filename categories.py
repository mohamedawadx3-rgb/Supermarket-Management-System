# إدارة تصنيفات المنتجات

import customtkinter as ctk
from tkinter import ttk, messagebox


class CategoriesPage(ctk.CTkFrame):

    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color="transparent")

        self.db = db
        self.app = app
        self.colors = app.colors
        self.selected_id = None

        self.create_interface()
        self.load_categories()

    # ترجمة النصوص حسب اللغة المختارة
    def t(self, english, arabic):
        return self.app.t(english, arabic)

    # ترجمة عناوين النوافذ المنبثقة بدون معالجة RTL
    def raw_t(self, english, arabic):
        return self.app.raw_t(english, arabic)

    # إنشاء الواجهة
    def create_interface(self):
        ctk.CTkLabel(
            self,
            text=self.t("Categories Management", "إدارة التصنيفات"),
            font=("Arial", 24, "bold"),
            text_color=self.colors["text"]
        ).pack(anchor="w", pady=15)

        form = ctk.CTkFrame(self, fg_color=self.colors["card"])
        form.pack(fill="x", pady=10)

        self.name_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Category Name", "اسم التصنيف"),
            width=250
        )
        self.name_entry.pack(side="left", padx=10, pady=15)

        self.description_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Description", "الوصف"),
            width=300
        )
        self.description_entry.pack(side="left", padx=10, pady=15)

        buttons = [
            (self.t("Add", "إضافة"), self.add_category),
            (self.t("Update", "تعديل"), self.update_category),
            (self.t("Delete", "حذف"), self.delete_category),
            (self.t("Clear", "مسح"), self.clear_fields)
        ]

        for title, command in buttons:
            ctk.CTkButton(
                form,
                text=title,
                command=command,
                width=85
            ).pack(side="left", padx=4)

        # قسم البحث
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self.t(
                "Search category", "ابحث عن تصنيف"
            )
        )
        self.search_entry.pack(
            side="left", fill="x", expand=True, padx=5
        )

        ctk.CTkButton(
            search_frame,
            text=self.t("Search", "بحث"),
            command=self.search_categories,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text=self.t("Show All", "عرض الكل"),
            command=self.load_categories,
            width=100
        ).pack(side="left", padx=5)

        # جدول التصنيفات
        self.tree = ttk.Treeview(
            self,
            columns=("id", "name", "description"),
            show="headings"
        )

        columns = [
            ("id", self.t("ID", "المعرف"), 80),
            ("name", self.t("Category Name", "اسم التصنيف"), 250),
            ("description", self.t("Description", "الوصف"), 400)
        ]

        for col, title, width in columns:
            self.tree.heading(col, text=title)
            self.tree.column(
                col,
                width=width,
                anchor="center"
            )

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_category
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

    # إضافة تصنيف
    def add_category(self):
        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()

        if not name:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Enter category name.",
                    "من فضلك أدخل اسم التصنيف."
                )
            )
            return

        success = self.execute_query(
            """INSERT INTO categories
               (category_name, description)
               VALUES (%s, %s)""",
            (name, description)
        )

        if success:
            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.t("Category added.", "تمت إضافة التصنيف.")
            )
            self.clear_fields()
            self.load_categories()

    # تحديد تصنيف من الجدول
    def select_category(self, event=None):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, values[1])

        self.description_entry.delete(0, "end")
        self.description_entry.insert(0, values[2] or "")

    # تعديل تصنيف
    def update_category(self):
        if not self.selected_id:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Select a category first.",
                    "من فضلك اختر تصنيفًا أولًا."
                )
            )
            return

        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()

        if not name:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Enter category name.",
                    "من فضلك أدخل اسم التصنيف."
                )
            )
            return

        success = self.execute_query(
            """UPDATE categories
               SET category_name=%s, description=%s
               WHERE category_id=%s""",
            (name, description, self.selected_id)
        )

        if success:
            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.t("Category updated.", "تم تعديل التصنيف.")
            )
            self.clear_fields()
            self.load_categories()

    # حذف تصنيف
    def delete_category(self):
        if not self.selected_id:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.t(
                    "Select a category first.",
                    "من فضلك اختر تصنيفًا أولًا."
                )
            )
            return

        confirm = messagebox.askyesno(
            self.raw_t("Confirm", "تأكيد"),
            self.t(
                "Delete this category?",
                "هل أنت متأكد من حذف هذا التصنيف؟"
            )
        )

        if confirm:
            success = self.execute_query(
                "DELETE FROM categories WHERE category_id=%s",
                (self.selected_id,)
            )

            if success:
                messagebox.showinfo(
                    self.raw_t("Success", "نجاح"),
                    self.t("Category deleted.", "تم حذف التصنيف.")
                )
                self.clear_fields()
                self.load_categories()

    # تحميل التصنيفات
    def load_categories(self):
        rows = self.execute_query(
            """SELECT category_id, category_name, description
               FROM categories
               ORDER BY category_id DESC""",
            fetch=True
        )

        if rows is not None:
            self.display_categories(rows)

    # البحث عن تصنيف
    def search_categories(self):
        keyword = self.search_entry.get().strip()

        rows = self.execute_query(
            """SELECT category_id, category_name, description
               FROM categories
               WHERE category_name LIKE %s
               ORDER BY category_id DESC""",
            (f"%{keyword}%",),
            fetch=True
        )

        if rows is not None:
            self.display_categories(rows)

    # عرض النتائج في الجدول
    def display_categories(self, rows):
        self.tree.delete(*self.tree.get_children())

        for row in rows:
            self.tree.insert("", "end", values=row)

    # تفريغ الحقول
    def clear_fields(self):
        self.name_entry.delete(0, "end")
        self.description_entry.delete(0, "end")
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())