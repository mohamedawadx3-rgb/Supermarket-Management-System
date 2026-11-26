# استدعاء مكتبة الاتصال بقاعدة بيانات MySQL
import mysql.connector

# استدعاء أداة التعامل مع أخطاء الاتصال
from mysql.connector import Error


# إنشاء كلاس مسؤول عن قاعدة البيانات بالكامل
class Database:

    # دالة إعداد الاتصال بقاعدة البيانات
    def __init__(self):

        # اسم السيرفر المحلي
        self.host = "localhost"

        # رقم منفذ MySQL الافتراضي
        self.port = 3306

        # اسم مستخدم قاعدة البيانات الافتراضي في XAMPP
        self.user = "root"

        # كلمة المرور الافتراضية في XAMPP
        self.password = ""

        # اسم قاعدة بيانات المشروع
        self.database = "supermarket_system"

    # دالة إنشاء الاتصال بسيرفر MySQL
    def connect_server(self):

        # الاتصال بالسيرفر بدون تحديد قاعدة بيانات
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password
        )

    # دالة الاتصال بقاعدة بيانات المشروع
    def get_connection(self):

        # إنشاء اتصال بقاعدة البيانات
        connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

        # إرجاع الاتصال لاستخدامه في باقي الملفات
        return connection

    # دالة إنشاء قاعدة البيانات والجداول
    def initialize_database(self):

        # إنشاء اتصال بالسيرفر
        connection = None
        cursor = None

        try:

            # الاتصال بسيرفر MySQL
            connection = self.connect_server()

            # إنشاء أداة تنفيذ أوامر SQL
            cursor = connection.cursor()

            # إنشاء قاعدة البيانات إذا لم تكن موجودة
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {self.database} "
                "CHARACTER SET utf8mb4 "
                "COLLATE utf8mb4_unicode_ci"
            )

            # إغلاق الاتصال الأول
            cursor.close()
            connection.close()

            # الاتصال بقاعدة بيانات المشروع
            connection = self.get_connection()

            # إنشاء أداة تنفيذ أوامر SQL
            cursor = connection.cursor()

            # قائمة الجداول الخاصة بالمشروع
            tables = [

                # جدول الأقسام
                """
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INT AUTO_INCREMENT PRIMARY KEY,
                    category_name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
                """,

                # جدول الموردين
                """
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
                    supplier_name VARCHAR(150) NOT NULL,
                    phone VARCHAR(30),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
                """,

                # جدول العملاء
                """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_name VARCHAR(150) NOT NULL,
                    phone VARCHAR(30),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
                """,

                # جدول المنتجات
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id INT AUTO_INCREMENT PRIMARY KEY,
                    product_name VARCHAR(150) NOT NULL,
                    barcode VARCHAR(100) UNIQUE,
                    category_id INT,
                    supplier_id INT,
                    purchase_price DECIMAL(12,2) DEFAULT 0,
                    selling_price DECIMAL(12,2) NOT NULL DEFAULT 0,
                    quantity INT NOT NULL DEFAULT 0,
                    min_quantity INT NOT NULL DEFAULT 5,
                    expiry_date DATE NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (category_id)
                    REFERENCES categories(category_id)
                    ON DELETE SET NULL,

                    FOREIGN KEY (supplier_id)
                    REFERENCES suppliers(supplier_id)
                    ON DELETE SET NULL
                ) ENGINE=InnoDB
                """,

                # جدول فواتير المبيعات
                """
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT NULL,
                    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
                    discount DECIMAL(12,2) NOT NULL DEFAULT 0,
                    total DECIMAL(12,2) NOT NULL DEFAULT 0,
                    paid_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
                    payment_method VARCHAR(50) DEFAULT 'Cash',
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
                    ON DELETE SET NULL
                ) ENGINE=InnoDB
                """,

                # جدول تفاصيل كل فاتورة مبيعات
                """
                CREATE TABLE IF NOT EXISTS sale_items (
                    item_id INT AUTO_INCREMENT PRIMARY KEY,
                    sale_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(12,2) NOT NULL,
                    item_total DECIMAL(12,2) NOT NULL,

                    FOREIGN KEY (sale_id)
                    REFERENCES sales(sale_id)
                    ON DELETE CASCADE,

                    FOREIGN KEY (product_id)
                    REFERENCES products(product_id)
                ) ENGINE=InnoDB
                """,

                # جدول فواتير المشتريات
                """
                CREATE TABLE IF NOT EXISTS purchases (
                    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
                    supplier_id INT NULL,
                    total DECIMAL(12,2) NOT NULL DEFAULT 0,
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (supplier_id)
                    REFERENCES suppliers(supplier_id)
                    ON DELETE SET NULL
                ) ENGINE=InnoDB
                """,

                # جدول تفاصيل المشتريات
                """
                CREATE TABLE IF NOT EXISTS purchase_items (
                    item_id INT AUTO_INCREMENT PRIMARY KEY,
                    purchase_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(12,2) NOT NULL,
                    item_total DECIMAL(12,2) NOT NULL,

                    FOREIGN KEY (purchase_id)
                    REFERENCES purchases(purchase_id)
                    ON DELETE CASCADE,

                    FOREIGN KEY (product_id)
                    REFERENCES products(product_id)
                ) ENGINE=InnoDB
                """,

                # جدول المصروفات
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id INT AUTO_INCREMENT PRIMARY KEY,
                    expense_name VARCHAR(150) NOT NULL,
                    amount DECIMAL(12,2) NOT NULL,
                    notes TEXT,
                    expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
                """,

                # جدول حركة المخزون
                """
                CREATE TABLE IF NOT EXISTS inventory_movements (
                    movement_id INT AUTO_INCREMENT PRIMARY KEY,
                    product_id INT NOT NULL,
                    movement_type VARCHAR(30) NOT NULL,
                    quantity INT NOT NULL,
                    notes TEXT,
                    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (product_id)
                    REFERENCES products(product_id)
                ) ENGINE=InnoDB
                """
            ]

            # المرور على أوامر إنشاء الجداول
            for table in tables:

                # تنفيذ أمر إنشاء الجدول
                cursor.execute(table)

            # حفظ التغييرات
            connection.commit()

            # إرجاع نتيجة نجاح إنشاء قاعدة البيانات
            return True

        except Error as error:

            # إظهار تفاصيل الخطأ عند حدوث مشكلة
            print("Database Error:", error)

            # التراجع عن التغييرات غير المحفوظة
            if connection and connection.is_connected():
                connection.rollback()

            # إرجاع نتيجة الفشل
            return False

        finally:

            # إغلاق أداة تنفيذ الأوامر
            if cursor:
                cursor.close()

            # إغلاق الاتصال بقاعدة البيانات
            if connection and connection.is_connected():
                connection.close()


# تشغيل اختبار قاعدة البيانات عند تشغيل هذا الملف مباشرة
if __name__ == "__main__":

    # إنشاء كائن من كلاس قاعدة البيانات
    db = Database()

    # إنشاء قاعدة البيانات والجداول
    if db.initialize_database():

        # طباعة رسالة نجاح
        print("Database and tables created successfully!")

    else:

        # طباعة رسالة فشل
        print("Database initialization failed!")