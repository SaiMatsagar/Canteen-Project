import os
import mysql.connector

# Connects WITHOUT selecting a database first, since the database
# might not exist yet on a brand-new Railway MySQL instance.
DB_NAME = os.getenv('MYSQLDATABASE', 'mess_db')

db = mysql.connector.connect(
    host=os.getenv('MYSQLHOST', 'localhost'),
    user=os.getenv('MYSQLUSER', 'root'),
    password=os.getenv('MYSQLPASSWORD', ''),
    port=int(os.getenv('MYSQLPORT', 3306))
)

cursor = db.cursor()

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
print("Database created.")

cursor.execute(f"USE {DB_NAME}")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(100),
        diet VARCHAR(20),
        membership_type VARCHAR(20) DEFAULT 'none',
        membership_status VARCHAR(20) DEFAULT 'none',
        transaction_id VARCHAR(100)
    )
""")
print("Students table created.")

# add phone column safely (only if it does not already exist)
try:
    cursor.execute("ALTER TABLE students ADD COLUMN phone VARCHAR(20)")
    print("Phone column added.")
except mysql.connector.Error:
    print("Phone column already exists.")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        id INT AUTO_INCREMENT PRIMARY KEY,
        meal_date DATE,
        meal_type VARCHAR(20),
        item_name VARCHAR(100),
        price INT,
        is_veg VARCHAR(10),
        available TINYINT(1) DEFAULT 1
    )
""")
print("Menu table created.")

# add available column safely (only if it does not already exist)
try:
    cursor.execute("ALTER TABLE menu ADD COLUMN available TINYINT(1) DEFAULT 1")
    print("Menu available column added.")
except mysql.connector.Error:
    print("Menu available column already exists.")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        menu_id INT,
        order_date DATE
    )
""")
print("Orders table created.")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS walkin_orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        customer_name VARCHAR(100),
        phone VARCHAR(20),
        item_names TEXT,
        total_amount INT,
        transaction_id VARCHAR(100),
        order_date DATE,
        delivered TINYINT(1) DEFAULT 0
    )
""")
print("Walkin orders table created.")

# add customer_name/phone columns safely (only if they do not already exist)
try:
    cursor.execute("ALTER TABLE walkin_orders ADD COLUMN customer_name VARCHAR(100)")
    print("Walkin customer_name column added.")
except mysql.connector.Error:
    print("Walkin customer_name column already exists.")

try:
    cursor.execute("ALTER TABLE walkin_orders ADD COLUMN phone VARCHAR(20)")
    print("Walkin phone column added.")
except mysql.connector.Error:
    print("Walkin phone column already exists.")

try:
    cursor.execute("ALTER TABLE walkin_orders ADD COLUMN student_id INT")
    print("Walkin student_id column added.")
except mysql.connector.Error:
    print("Walkin student_id column already exists.")

try:
    cursor.execute("ALTER TABLE walkin_orders ADD COLUMN delivered TINYINT(1) DEFAULT 0")
    print("Walkin delivered column added.")
except mysql.connector.Error:
    print("Walkin delivered column already exists.")

db.commit()
cursor.close()
db.close()

print("All done. Now run app.py")
