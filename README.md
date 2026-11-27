Supermarket Management System

A desktop-based Supermarket Management System developed using Python, CustomTkinter, and MySQL. The application provides a graphical user interface for managing supermarket operations, organizing data, and monitoring sales and inventory.

Features

- Dashboard: View important supermarket statistics and recent sales.
- Products Management: Add, update, delete, search, and display products.
- Categories Management: Manage product categories.
- Sales Management: Manage sales transactions.
- Customers Management: Store and manage customer information.
- Suppliers Management: Manage supplier information.
- Inventory Management: Monitor inventory information and movements.
- Reports: View sales reports and statistics.
- Settings: Change the application language and test the database connection.
- Bilingual Interface: Supports English and Arabic.

Technologies Used

- Python
- CustomTkinter
- Tkinter
- MySQL
- MySQL Connector
- Arabic Reshaper
- Python Bidi

Project Structure

supermarket_management_sestem/
│
├── main.py
├── app.py
├── database.py
├── language.py
├── dashboard.py
├── products.py
├── categories.py
├── sales.py
├── customers.py
├── suppliers.py
├── inventory.py
├── reports.py
├── settings.py
│
├── language.json
├── requirements.txt
├── README.md
└── .gitignore

Requirements

- Python 3.10 or later
- XAMPP or another MySQL/MariaDB server
- Required Python libraries listed in "requirements.txt"

Installation and Setup

1. Clone the Repository

git clone YOUR_REPOSITORY_URL

2. Navigate to the Project Directory

cd supermarket_management_sestem

3. Install Dependencies

pip install -r requirements.txt

4. Start the Database Server

- Open XAMPP.
- Start MySQL.
- Make sure the database connection settings in "database.py" match your local environment.

The application initializes the database and creates the required tables automatically when it starts.

5. Run the Application

python main.py

Database

The project uses MySQL/MariaDB to store application data.

The database name is:

supermarket_system

Database tables are initialized automatically through the "database.py" module.

Language Support

The application supports:

- English
- Arabic

Users can change the application language through the Settings page.

Author

Engineer Mohamed Awad

---

Supermarket Management System
Python | CustomTkinter | MySQL
