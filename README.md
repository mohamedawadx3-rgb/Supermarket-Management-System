Supermarket Management System

A desktop-based Supermarket Management System developed using Python, CustomTkinter, and MySQL. The application provides an organized graphical interface for managing supermarket operations, maintaining records, tracking inventory, and monitoring sales activities.

Features

- Dashboard: Displays key supermarket statistics, including product count, inventory quantity, customer count, monthly sales, and recent transactions.
- Products Management: Add, update, delete, search, and display product information.
- Categories Management: Organize and manage product categories.
- Sales Management: Manage sales transactions and related sale details.
- Customers Management: Add, update, delete, search, and manage customer records.
- Suppliers Management: Maintain supplier information and records.
- Inventory Management: Monitor stock quantities and inventory movements.
- Reports & Statistics: View sales reports and business statistics.
- Database Management: Automatically initialize the database and create the required tables.
- Settings: Change the application language and test the database connection.
- Bilingual Interface: Supports both Arabic and English.
- Data Validation: Validate user inputs and prevent invalid values in supported forms.
- Search Functionality: Quickly find records using search fields.

Technologies Used

- Python
- Object-Oriented Programming (OOP)
- CustomTkinter
- Tkinter
- MySQL / MariaDB
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
│
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

Database Name:

supermarket_system

The database tables are initialized automatically through the "database.py" module.

Language Support

The application supports:

- English
- Arabic

Users can change the application language through the Settings page.

Author

Engineer Mohamed Awad

Developed as an academic Python Management System project.

---

Supermarket Management System
Python | CustomTkinter | MySQL
