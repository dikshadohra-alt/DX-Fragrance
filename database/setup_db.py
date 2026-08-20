import sqlite3
import os

# Check the database file path
db_path = os.path.join('database', 'dx_fragrance.db')
print(f"Connecting to database at: {db_path}")

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Users Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0
)
''')

# Products / Perfumes Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    description TEXT,
    image TEXT
)
''')

# Orders Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    total_price REAL NOT NULL,
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Notifications Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

connection.commit()
connection.close()
print("🎉 All tables have been created successfully!")

# Store Settings Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS store_settings (
    id INTEGER PRIMARY KEY,
    store_name TEXT,
    store_email TEXT,
    store_phone TEXT,
    store_address TEXT,
    whatsapp TEXT,
    instagram TEXT,
    facebook TEXT,
    youtube TEXT
)
''')