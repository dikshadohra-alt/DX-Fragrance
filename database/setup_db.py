import sqlite3
import os


# ============================================================
# DATABASE PATH
# ============================================================

db_path = os.path.join(
    "database",
    "dx_fragrance.db"
)

print(
    f"Connecting to database at: {db_path}"
)


# ============================================================
# CONNECT DATABASE
# ============================================================

connection = sqlite3.connect(
    db_path
)

cursor = connection.cursor()


# ============================================================
# USERS TABLE
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0
    )
    """
)


# ============================================================
# PRODUCTS TABLE (With slug column)
# ============================================================

cursor.execute(
    """
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
        fragrance_notes TEXT
    )
    """
)


# ============================================================
# PRODUCT TABLE MIGRATION & SAFE COLUMNS
# ============================================================

try:
    cursor.execute(
        """
        ALTER TABLE products
        ADD COLUMN slug TEXT
        """
    )
    print("Added products.slug column.")
except sqlite3.OperationalError:
    pass


try:
    cursor.execute(
        """
        ALTER TABLE products
        ADD COLUMN status TEXT DEFAULT 'active'
        """
    )
    print("Added products.status column.")
except sqlite3.OperationalError:
    pass


try:
    cursor.execute(
        """
        ALTER TABLE products
        ADD COLUMN fragrance_notes TEXT
        """
    )
    print("Added products.fragrance_notes column.")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute(
        """
        ALTER TABLE products
        ADD COLUMN size_ml TEXT
        """
    )
    print("Added products.size_ml column.")
except sqlite3.OperationalError:
    pass

# Existing products ko active kar do agar status khali hai
cursor.execute(
    """
    UPDATE products
    SET status = 'active'
    WHERE status IS NULL
       OR status = ''
    """
)


# ============================================================
# ORDERS TABLE (With total_amount and total_price safety)
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total_price REAL NOT NULL DEFAULT 0.0,
        total_amount REAL,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id)
        REFERENCES users (id)
    )
    """
)

# Migration for orders total_amount just in case
try:
    cursor.execute(
        """
        ALTER TABLE orders
        ADD COLUMN total_amount REAL
        """
    )
    print("Added orders.total_amount column.")
except sqlite3.OperationalError:
    pass


# ============================================================
# REVIEWS TABLE (Added to fix admin reviews 500 error)
# ============================================================

cursor.execute(
    """
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


# ============================================================
# WISHLIST TABLE
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """
)


# ============================================================
# NOTIFICATIONS TABLE
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)


# ============================================================
# STORE SETTINGS TABLE
# ============================================================

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


# ============================================================
# DEFAULT STORE SETTINGS
# ============================================================

cursor.execute(
    """
    INSERT OR IGNORE INTO store_settings (
        id,
        store_name,
        store_email,
        store_phone,
        store_address,
        whatsapp,
        instagram,
        facebook,
        youtube
    )
    VALUES (
        1,
        'DX Fragrance',
        '',
        '',
        '',
        '',
        '',
        '',
        ''
    )
    """
)


# ============================================================
# SAVE DATABASE & CLOSE
# ============================================================

connection.commit()
connection.close()

print(
    "🎉 All tables and columns have been created and verified successfully!"
)