import os
import mysql.connector

# Reads DB details from environment variables (set by Railway automatically
# when you attach a MySQL database there). Falls back to local XAMPP/MySQL
# settings so this still works on your own laptop with no extra setup.

def get_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST', 'localhost'),
        user=os.getenv('MYSQLUSER', 'root'),
        password=os.getenv('MYSQLPASSWORD', ''),
        database=os.getenv('MYSQLDATABASE', 'mess_db'),
        port=int(os.getenv('MYSQLPORT', 3306))
    )
