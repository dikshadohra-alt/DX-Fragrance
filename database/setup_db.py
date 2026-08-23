import sys
import os

# Root folder ko Python path mein add karne ke liye
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import sqlite3
from config.database import get_db_connection, DATABASE_URL

print("Setting up database tables...")

connection = get_db_connection()
cursor = connection.cursor()

# 1. USERS TABLE
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE
    )
    """ if DATABASE_URL else """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0
    )
    """
)

# 2. PRODUCTS TABLE
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        slug TEXT,
        category TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        description TEXT,
        image TEXT,
        status TEXT DEFAULT 'active',
        fragrance_notes TEXT,
        size_ml TEXT
    )
    """ if DATABASE_URL else """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT,
        category TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        description TEXT,
        image TEXT,
        status TEXT DEFAULT 'active',
        fragrance_notes TEXT,
        size_ml TEXT
    )
    """
)

# 3. ORDERS TABLE
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        total_price REAL NOT NULL DEFAULT 0.0,
        total_amount REAL,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """ if DATABASE_URL else """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total_price REAL NOT NULL DEFAULT 0.0,
        total_amount REAL,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
)

# 4. REVIEWS TABLE
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        product_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
    )
    """ if DATABASE_URL else """
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
    )
    """
)

# 5. WISHLIST TABLE
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS wishlist (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """ if DATABASE_URL else """
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """
)

# 6. NOTIFICATIONS TABLE
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id SERIAL PRIMARY KEY,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """ if DATABASE_URL else """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

# 7. STORE SETTINGS TABLE
cursor.execute(
    """
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
    """
)

connection.commit()
connection.close()

print("🎉 All PostgreSQL/SQLite tables created successfully!")