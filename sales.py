# ============================================================
# Sales Management System
# إدارة المبيعات والمرتجعات
# ============================================================

import customtkinter as ctk
from tkinter import messagebox, ttk
from decimal import Decimal, InvalidOperation
from mysql.connector import Error
import arabic_reshaper
from bidi.algorithm import get_display


class SalesPage(ctk.CTkFrame):

    def __init__(self, parent, db, app):
        super().__init__(parent)

        self.db = db
        self.app = app
        self.cart = []
        self.products = []
        self.product_labels = {}
        self.return_data = {}
        self.current_invoice = None

        self.ensure_return_tables()
        self.create_interface()
        self.load_products()

    # ========================================================
    # الترجمة ومعالجة النصوص
    # ========================================================

    def t(self, english, arabic=None):
        return self.app.t(english, arabic)

    def raw_t(self, english, arabic=None):
        return self.app.raw_t(english, arabic)

    # معالجة النصوص للقائمة العلوية
    def rtl(self, text):
        text = str(text)

        if self.app.language != "العربية":
            return text

        if not any("\u0600" <= c <= "\u06FF" for c in text):
            return text

        return get_display(
            arabic_reshaper.reshape(text),
            base_dir="R"
        )

    # تشكيل الحروف فقط للجداول
    def tree_text(self, text):
        text = str(text)

        if self.app.language != "العربية":
            return text

        if not any("\u0600" <= c <= "\u06FF" for c in text):
            return text

        return arabic_reshaper.reshape(text)

    # تحويل القيم المالية
    def amount(self, value):
        return f"{Decimal(str(value)):.2f}"

    def get_amount(self, value):
        value = str(value).strip()
        value = value.translate(str.maketrans(
            "٠١٢٣٤٥٦٧٨٩", "0123456789"
        ))
        value = value.replace("٫", ".").replace("٬", "")

        if "," in value and "." not in value:
            value = value.replace(",", ".")

        return Decimal(value or "0")

    # ========================================================
    # إنشاء جداول المرتجعات
    # ========================================================

    def ensure_return_tables(self):

        connection = None
        cursor = None

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales_returns (
                    return_id INT AUTO_INCREMENT PRIMARY KEY,
                    sale_id INT NOT NULL,
                    return_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    refund_amount DECIMAL(12,2) NOT NULL,
                    notes VARCHAR(255),
                    FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
                ) ENGINE=InnoDB
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales_return_items (
                    return_item_id INT AUTO_INCREMENT PRIMARY KEY,
                    return_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(12,2) NOT NULL,
                    item_total DECIMAL(12,2) NOT NULL,
                    FOREIGN KEY (return_id)
                        REFERENCES sales_returns(return_id),
                    FOREIGN KEY (product_id)
                        REFERENCES products(product_id)
                ) ENGINE=InnoDB
            """)

            connection.commit()

        except Error as error:
            if connection:
                connection.rollback()

            messagebox.showerror(
                self.raw_t("Returns Setup Error", "خطأ في إعداد المرتجعات"),
                str(error)
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # ========================================================
    # واجهة المبيعات
    # ========================================================

    def create_interface(self):

        ctk.CTkLabel(
            self,
            text=self.t("Sales Management", "إدارة المبيعات"),
            font=("Arial", 24, "bold")
        ).pack(pady=12)

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=8)

        for col in range(4):
            form.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(
            form, text=self.t("Product", "المنتج")
        ).grid(row=0, column=0, padx=8, pady=(10, 3))

        self.product_menu = ctk.CTkComboBox(
            form,
            values=[self.t("Loading...", "جاري التحميل...")],
            width=250,
            justify="right",
            state="readonly"
        )
        self.product_menu.grid(
            row=1, column=0, padx=8, pady=(3, 12), sticky="ew"
        )

        ctk.CTkLabel(
            form, text=self.t("Quantity", "الكمية")
        ).grid(row=0, column=1, padx=8, pady=(10, 3))

        self.quantity_entry = ctk.CTkEntry(
            form,
            placeholder_text=self.t("Quantity", "الكمية")
        )
        self.quantity_entry.grid(
            row=1, column=1, padx=8, pady=(3, 12), sticky="ew"
        )

        ctk.CTkButton(
            form,
            text=self.t("Add to Cart", "إضافة إلى السلة"),
            command=self.add_to_cart
        ).grid(row=1, column=2, padx=8, pady=(3, 12), sticky="ew")

        # جدول الفاتورة
        self.table = ttk.Treeview(
            self,
            columns=("id", "name", "quantity", "price", "total"),
            show="headings",
            height=9
        )

        columns = [
            ("id", self.t("ID", "الرقم")),
            ("name", self.t("Product", "المنتج")),
            ("quantity", self.t("Quantity", "الكمية")),
            ("price", self.t("Unit Price", "سعر الوحدة")),
            ("total", self.t("Total", "الإجمالي"))
        ]

        for col, title in columns:
            self.table.heading(col, text=title)
            self.table.column(
                col, width=120, anchor="center", stretch=False
            )

        self.table.column("name", width=240)
        self.table.pack(fill="both", expand=True, padx=20, pady=8)

        # بيانات الدفع
        details = ctk.CTkFrame(self)
        details.pack(fill="x", padx=20, pady=8)

        for col in range(6):
            details.grid_columnconfigure(col, weight=1)

        self.discount_entry = ctk.CTkEntry(
            details,
            placeholder_text=self.t("Discount", "الخصم"),
            width=120
        )
        self.discount_entry.grid(
            row=0, column=0, padx=6, pady=12, sticky="ew"
        )

        self.payment_values = {
            self.t("Cash", "نقدي"): "Cash",
            self.t("Card", "بطاقة"): "Card",
            self.t("Wallet", "محفظة"): "Wallet"
        }

        self.payment_menu = ctk.CTkOptionMenu(
            details,
            values=list(self.payment_values.keys()),
            width=120
        )
        self.payment_menu.grid(
            row=0, column=1, padx=6, pady=12, sticky="ew"
        )

        self.paid_entry = ctk.CTkEntry(
            details,
            placeholder_text=self.t("Paid Amount", "المبلغ المدفوع"),
            width=130
        )
        self.paid_entry.grid(
            row=0, column=2, padx=6, pady=12, sticky="ew"
        )

        ctk.CTkButton(
            details,
            text=self.t("Calculate", "حساب"),
            command=self.calculate_total
        ).grid(row=0, column=3, padx=6, pady=12, sticky="ew")

        self.total_label = self.create_amount_box(
            details, 4, "Total", "الإجمالي"
        )
        self.change_label = self.create_amount_box(
            details, 5, "Change", "المتبقي"
        )

        # أزرار التحكم
        actions = ctk.CTkFrame(self)
        actions.pack(fill="x", padx=20, pady=8)

        buttons = [
            ("Remove Item", "حذف المنتج", self.remove_item),
            ("Complete Sale", "إتمام البيع", self.complete_sale),
            ("Clear Cart", "تفريغ السلة", self.clear_cart),
            ("Returns", "المرتجعات", self.open_returns)
        ]

        for english, arabic, command in buttons:
            ctk.CTkButton(
                actions,
                text=self.t(english, arabic),
                command=command
            ).pack(side="left", padx=8, pady=10)

    # عرض اسم الإجمالي منفصلًا عن الرقم
    def create_amount_box(self, parent, column, english, arabic):

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(
            frame,
            text=self.rtl(self.raw_t(english, arabic)),
            font=("Arial", 13, "bold")
        ).pack(side="right", padx=3)

        value_label = ctk.CTkLabel(
            frame,
            text="0.00",
            font=("Arial", 13, "bold")
        )
        value_label.pack(side="left", padx=3)

        return value_label

    def set_amount(self, label, value):
        label.configure(text=self.amount(value))

    # ========================================================
    # تحميل المنتجات
    # ========================================================

    def load_products(self):

        connection = None
        cursor = None

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT product_id, product_name, selling_price, quantity
                FROM products
                WHERE quantity > 0
                ORDER BY product_name
            """)

            self.products = cursor.fetchall()
            self.product_labels.clear()
            names = []

            for product in self.products:
                product_id = product[0]
                label = f"{product_id} - {self.rtl(product[1])}"

                self.product_labels[label] = product_id
                names.append(label)

            if names:
                self.product_menu.configure(values=names)
                self.product_menu.set(names[0])
            else:
                empty = self.t("No Products", "لا توجد منتجات")
                self.product_menu.configure(values=[empty])
                self.product_menu.set(empty)

        except Error as error:
            messagebox.showerror(
                self.raw_t("Database Error", "خطأ في قاعدة البيانات"),
                str(error)
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # ========================================================
    # إضافة منتج للسلة
    # ========================================================

    def add_to_cart(self):

        if not self.products:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t("No products available", "لا توجد منتجات متاحة للبيع")
            )
            return

        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t("Enter a valid quantity", "أدخل كمية صحيحة")
            )
            return

        product_id = self.product_labels.get(self.product_menu.get())
        product = next(
            (p for p in self.products if p[0] == product_id),
            None
        )

        if not product:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t("Select a valid product", "اختر منتجًا صحيحًا")
            )
            return

        product_id, name, price, stock = product

        existing = sum(
            x["quantity"] for x in self.cart
            if x["id"] == product_id
        )

        if existing + quantity > stock:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Not enough stock available",
                    "الكمية الموجودة في المخزون غير كافية"
                )
            )
            return

        item = next(
            (x for x in self.cart if x["id"] == product_id),
            None
        )

        if item:
            item["quantity"] += quantity
            item["total"] = item["price"] * item["quantity"]
        else:
            price = Decimal(str(price))
            self.cart.append({
                "id": product_id,
                "name": name,
                "quantity": quantity,
                "price": price,
                "total": price * quantity
            })

        self.refresh_cart()
        self.quantity_entry.delete(0, "end")

    # تحديث جدول السلة
    def refresh_cart(self):

        for row in self.table.get_children():
            self.table.delete(row)

        for item in self.cart:
            self.table.insert(
                "",
                "end",
                values=(
                    item["id"],
                    self.tree_text(item["name"]),
                    item["quantity"],
                    self.amount(item["price"]),
                    self.amount(item["total"])
                )
            )

        self.calculate_total(False)

    # ========================================================
    # حساب الفاتورة
    # ========================================================

    def calculate_total(self, show_warning=True):

        try:
            subtotal = sum(
                (x["total"] for x in self.cart),
                Decimal("0")
            )

            discount = self.get_amount(self.discount_entry.get())
            paid = self.get_amount(self.paid_entry.get())

            if discount < 0 or paid < 0:
                raise ValueError

            if discount > subtotal:
                if show_warning:
                    messagebox.showwarning(
                        self.raw_t("Warning", "تنبيه"),
                        self.raw_t(
                            "Discount cannot exceed subtotal.",
                            "الخصم لا يمكن أن يتجاوز إجمالي المنتجات."
                        )
                    )
                return None

            total = subtotal - discount
            change = max(Decimal("0"), paid - total)

            self.set_amount(self.total_label, total)
            self.set_amount(self.change_label, change)

            return subtotal, discount, total, paid

        except (ValueError, InvalidOperation):
            if show_warning:
                messagebox.showwarning(
                    self.raw_t("Warning", "تنبيه"),
                    self.raw_t(
                        "Enter valid discount and paid amount",
                        "أدخل قيمة صحيحة للخصم والمبلغ المدفوع"
                    )
                )
            return None

    # حذف منتج من السلة
    def remove_item(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Select an item to remove",
                    "اختر منتجًا لحذفه من السلة"
                )
            )
            return

        index = self.table.index(selected[0])

        if 0 <= index < len(self.cart):
            del self.cart[index]

        self.refresh_cart()

    # تفريغ السلة
    def clear_cart(self):

        self.cart.clear()
        self.refresh_cart()

        self.discount_entry.delete(0, "end")
        self.paid_entry.delete(0, "end")

        self.set_amount(self.total_label, 0)
        self.set_amount(self.change_label, 0)
        # ========================================================
    # إتمام البيع
    # ========================================================

    def complete_sale(self):

        if not self.cart:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t("Cart is empty", "سلة البيع فارغة")
            )
            return

        result = self.calculate_total()

        if result is None:
            return

        subtotal, discount, total, paid = result

        if paid < total:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Paid amount is less than total",
                    "المبلغ المدفوع أقل من إجمالي الفاتورة"
                )
            )
            return

        payment_method = self.payment_values.get(
            self.payment_menu.get(), "Cash"
        )

        connection = None
        cursor = None

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            connection.start_transaction()

            # التأكد من توفر الكميات
            for item in self.cart:
                cursor.execute(
                    """
                    SELECT quantity FROM products
                    WHERE product_id = %s FOR UPDATE
                    """,
                    (item["id"],)
                )

                stock = cursor.fetchone()

                if not stock or stock[0] < item["quantity"]:
                    raise ValueError(
                        self.raw_t(
                            "Not enough stock for",
                            "المخزون غير كافٍ للمنتج"
                        ) + ": " + str(item["name"])
                    )

            # إنشاء الفاتورة
            cursor.execute(
                """
                INSERT INTO sales
                (subtotal, discount, total, paid_amount, payment_method)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (subtotal, discount, total, paid, payment_method)
            )

            sale_id = cursor.lastrowid

            # حفظ تفاصيل البيع وتحديث المخزون
            for item in self.cart:

                cursor.execute(
                    """
                    INSERT INTO sale_items
                    (sale_id, product_id, quantity, unit_price, item_total)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        sale_id,
                        item["id"],
                        item["quantity"],
                        item["price"],
                        item["total"]
                    )
                )

                cursor.execute(
                    """
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE product_id = %s
                    """,
                    (item["quantity"], item["id"])
                )

                cursor.execute(
                    """
                    INSERT INTO inventory_movements
                    (product_id, movement_type, quantity, notes)
                    VALUES (%s, 'OUT', %s, %s)
                    """,
                    (
                        item["id"],
                        item["quantity"],
                        f"Sale Invoice #{sale_id}"
                    )
                )

            connection.commit()

            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.raw_t(
                    "Sale completed successfully",
                    "تم إتمام عملية البيع بنجاح"
                )
                + f"\n{self.raw_t('Invoice ID', 'رقم الفاتورة')}: {sale_id}"
                + f"\n{self.raw_t('Total', 'الإجمالي')}: {total:.2f}"
                + f"\n{self.raw_t('Change', 'المتبقي')}: {paid - total:.2f}"
            )

            self.clear_cart()
            self.load_products()

        except (Error, ValueError) as error:
            if connection:
                connection.rollback()

            messagebox.showerror(
                self.raw_t("Sale Error", "خطأ في البيع"),
                str(error)
            )

        except Exception as error:
            if connection:
                connection.rollback()

            messagebox.showerror(
                self.raw_t("Unexpected Error", "خطأ غير متوقع"),
                str(error)
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # ========================================================
    # نافذة المرتجعات
    # ========================================================

    def open_returns(self):

        self.return_window = ctk.CTkToplevel(self)
        self.return_window.title(
            self.t("Sales Returns", "مرتجعات المبيعات")
        )
        self.return_window.geometry("950x620")
        self.return_window.minsize(800, 500)
        self.return_window.grab_set()

        ctk.CTkLabel(
            self.return_window,
            text=self.t("Manage Sales Returns", "إدارة مرتجعات المبيعات"),
            font=("Arial", 22, "bold")
        ).pack(pady=12)

        # البحث برقم الفاتورة
        search_frame = ctk.CTkFrame(self.return_window)
        search_frame.pack(fill="x", padx=15, pady=8)

        self.return_invoice_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self.t("Invoice Number", "رقم الفاتورة"),
            width=180
        )
        self.return_invoice_entry.pack(
            side="right", padx=8, pady=12
        )

        ctk.CTkButton(
            search_frame,
            text=self.t("Search Invoice", "بحث عن الفاتورة"),
            command=self.load_return_invoice
        ).pack(side="right", padx=8, pady=12)

        self.return_info = ctk.CTkLabel(
            self.return_window,
            text=self.t(
                "Enter an invoice number to search",
                "أدخل رقم الفاتورة للبحث"
            )
        )
        self.return_info.pack(pady=8)

        # جدول منتجات الفاتورة
        self.return_table = ttk.Treeview(
            self.return_window,
            columns=(
                "id", "name", "sold", "returned",
                "remaining", "price"
            ),
            show="headings",
            height=12
        )

        columns = [
            ("id", self.t("ID", "الرقم")),
            ("name", self.t("Product", "المنتج")),
            ("sold", self.t("Sold", "المباع")),
            ("returned", self.t("Returned", "المرتجع")),
            ("remaining", self.t("Returnable", "المتاح للإرجاع")),
            ("price", self.t("Refund Price", "سعر الاسترداد"))
        ]

        for col, title in columns:
            self.return_table.heading(col, text=title)
            self.return_table.column(
                col, width=130, anchor="center"
            )

        self.return_table.column("name", width=220)
        self.return_table.pack(
            fill="both", expand=True, padx=15, pady=8
        )

        # كمية المرتجع
        controls = ctk.CTkFrame(self.return_window)
        controls.pack(fill="x", padx=15, pady=10)

        self.return_quantity = ctk.CTkEntry(
            controls,
            placeholder_text=self.t(
                "Return Quantity", "كمية المرتجع"
            ),
            width=160
        )
        self.return_quantity.pack(
            side="right", padx=8, pady=12
        )

        ctk.CTkButton(
            controls,
            text=self.t("Confirm Return", "تأكيد المرتجع"),
            command=self.process_return
        ).pack(side="right", padx=8, pady=12)

    # ========================================================
    # البحث عن فاتورة
    # ========================================================

    def load_return_invoice(self):

        try:
            sale_id = int(self.return_invoice_entry.get())

            if sale_id <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Enter a valid invoice number",
                    "أدخل رقم فاتورة صحيحًا"
                )
            )
            return

        connection = None
        cursor = None

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT sale_id, subtotal, discount, total
                FROM sales
                WHERE sale_id = %s
                """,
                (sale_id,)
            )

            sale = cursor.fetchone()

            if not sale:
                messagebox.showwarning(
                    self.raw_t("Warning", "تنبيه"),
                    self.raw_t(
                        "Invoice not found",
                        "الفاتورة غير موجودة"
                    )
                )
                return

            cursor.execute(
                """
                SELECT
                    p.product_id,
                    p.product_name,
                    SUM(si.quantity),
                    SUM(si.item_total)
                FROM sale_items si
                JOIN products p ON p.product_id = si.product_id
                WHERE si.sale_id = %s
                GROUP BY p.product_id, p.product_name
                """,
                (sale_id,)
            )

            products = cursor.fetchall()

            cursor.execute(
                """
                SELECT sri.product_id, SUM(sri.quantity)
                FROM sales_return_items sri
                JOIN sales_returns sr
                    ON sr.return_id = sri.return_id
                WHERE sr.sale_id = %s
                GROUP BY sri.product_id
                """,
                (sale_id,)
            )

            returned = dict(cursor.fetchall())

            for row in self.return_table.get_children():
                self.return_table.delete(row)

            self.return_data.clear()
            self.current_invoice = sale_id

            subtotal = Decimal(str(sale[1]))
            total = Decimal(str(sale[3]))

            factor = total / subtotal if subtotal > 0 else Decimal("1")

            for product_id, name, sold, gross_total in products:

                returned_qty = returned.get(product_id, 0)
                remaining = sold - returned_qty

                unit_price = (
                    Decimal(str(gross_total))
                    / Decimal(str(sold))
                    * factor
                )

                self.return_data[product_id] = {
                    "name": name,
                    "sold": sold,
                    "returned": returned_qty,
                    "remaining": remaining,
                    "price": unit_price
                }

                self.return_table.insert(
                    "",
                    "end",
                    iid=str(product_id),
                    values=(
                        product_id,
                        self.tree_text(name),
                        sold,
                        returned_qty,
                        remaining,
                        self.amount(unit_price)
                    )
                )

            self.return_info.configure(
                text=(
                    self.raw_t("Invoice", "الفاتورة")
                    + f" #{sale_id}   |   "
                    + self.raw_t("Total", "الإجمالي")
                    + f": {self.amount(total)}"
                )
            )

        except Error as error:
            messagebox.showerror(
                self.raw_t("Database Error", "خطأ في قاعدة البيانات"),
                str(error)
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # ========================================================
    # تنفيذ المرتجع
    # ========================================================

    def process_return(self):

        if not self.current_invoice:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Search for an invoice first",
                    "ابحث عن الفاتورة أولًا"
                )
            )
            return

        selected = self.return_table.selection()

        if not selected:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Select a product to return",
                    "اختر المنتج المراد إرجاعه"
                )
            )
            return

        try:
            quantity = int(self.return_quantity.get())

            if quantity <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                self.raw_t("Warning", "تنبيه"),
                self.raw_t(
                    "Enter a valid return quantity",
                    "أدخل كمية مرتجع صحيحة"
                )
            )
            return

        product_id = int(selected[0])
        connection = None
        cursor = None

        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            connection.start_transaction()

            # قفل الفاتورة لمنع تكرار المرتجع بالتزامن
            cursor.execute(
                """
                SELECT subtotal, discount, total
                FROM sales
                WHERE sale_id = %s
                FOR UPDATE
                """,
                (self.current_invoice,)
            )

            sale = cursor.fetchone()

            if not sale:
                raise ValueError(
                    self.raw_t("Invoice not found", "الفاتورة غير موجودة")
                )

            # الكمية الأصلية وقيمة المنتج
            cursor.execute(
                """
                SELECT COALESCE(SUM(quantity), 0),
                       COALESCE(SUM(item_total), 0)
                FROM sale_items
                WHERE sale_id = %s AND product_id = %s
                """,
                (self.current_invoice, product_id)
            )

            sold, gross_total = cursor.fetchone()

            # الكمية المرتجعة سابقًا
            cursor.execute(
                """
                SELECT COALESCE(SUM(sri.quantity), 0)
                FROM sales_return_items sri
                JOIN sales_returns sr
                    ON sr.return_id = sri.return_id
                WHERE sr.sale_id = %s AND sri.product_id = %s
                """,
                (self.current_invoice, product_id)
            )

            already_returned = cursor.fetchone()[0]
            remaining = sold - already_returned

            if quantity > remaining:
                raise ValueError(
                    self.raw_t(
                        "Return quantity exceeds the remaining quantity",
                        "كمية المرتجع أكبر من الكمية المتاحة للإرجاع"
                    )
                )

            # حساب قيمة المرتجع بعد الخصم
            subtotal = Decimal(str(sale[0]))
            total = Decimal(str(sale[2]))

            factor = total / subtotal if subtotal > 0 else Decimal("1")

            unit_price = (
                Decimal(str(gross_total))
                / Decimal(str(sold))
                * factor
            )

            refund = (unit_price * quantity).quantize(
                Decimal("0.01")
            )

            # تسجيل المرتجع
            cursor.execute(
                """
                INSERT INTO sales_returns
                (sale_id, refund_amount, notes)
                VALUES (%s, %s, %s)
                """,
                (
                    self.current_invoice,
                    refund,
                    "Customer product return"
                )
            )

            return_id = cursor.lastrowid

            # تفاصيل المرتجع
            cursor.execute(
                """
                INSERT INTO sales_return_items
                (return_id, product_id, quantity, unit_price, item_total)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    return_id,
                    product_id,
                    quantity,
                    unit_price,
                    refund
                )
            )

            # إعادة الكمية للمخزون
            cursor.execute(
                """
                UPDATE products
                SET quantity = quantity + %s
                WHERE product_id = %s
                """,
                (quantity, product_id)
            )

            # تسجيل حركة المخزون
            cursor.execute(
                """
                INSERT INTO inventory_movements
                (product_id, movement_type, quantity, notes)
                VALUES (%s, 'IN', %s, %s)
                """,
                (
                    product_id,
                    quantity,
                    f"Sales Return #{return_id}"
                )
            )

            connection.commit()

            messagebox.showinfo(
                self.raw_t("Success", "نجاح"),
                self.raw_t(
                    "Return completed successfully",
                    "تم تسجيل المرتجع بنجاح"
                )
                + f"\n{self.raw_t('Return Number', 'رقم المرتجع')}: {return_id}"
                + f"\n{self.raw_t('Refund Amount', 'المبلغ المسترد')}: {refund:.2f}"
            )

            self.return_quantity.delete(0, "end")
            self.load_return_invoice()
            self.load_products()

        except (Error, ValueError) as error:
            if connection:
                connection.rollback()

            messagebox.showerror(
                self.raw_t("Return Error", "خطأ في المرتجع"),
                str(error)
            )

        except Exception as error:
            if connection:
                connection.rollback()

            messagebox.showerror(
                self.raw_t("Unexpected Error", "خطأ غير متوقع"),
                str(error)
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()