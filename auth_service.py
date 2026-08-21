import sqlite3
import os


class AuthService:

    @staticmethod
    def get_db_connection():

        db_dir = os.path.join(
            os.getcwd(),
            "database"
        )

        os.makedirs(
            db_dir,
            exist_ok=True
        )

        db_path = os.path.join(
            db_dir,
            "dx_fragrance.db"
        )

        connection = sqlite3.connect(db_path)

        connection.row_factory = sqlite3.Row

        # Create users table if it does not exist
        connection.execute(
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

        # Make sure default admin exists
        admin = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            ("admin@dxfragrance.com",)
        ).fetchone()

        if not admin:

            connection.execute(
                """
                INSERT INTO users
                (username, email, password, is_admin)
                VALUES (?, ?, ?, ?)
                """,
                (
                    "Admin",
                    "admin@dxfragrance.com",
                    "DXAdmin@2026",
                    1
                )
            )

        else:

            # Reset default admin credentials
            connection.execute(
                """
                UPDATE users
                SET password = ?,
                    is_admin = 1
                WHERE email = ?
                """,
                (
                    "DXAdmin@2026",
                    "admin@dxfragrance.com"
                )
            )

        connection.commit()

        return connection


    @staticmethod
    def login(email, password):

        connection = AuthService.get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
            """,
            (
                email,
                password
            )
        ).fetchone()

        connection.close()

        return user

    @staticmethod
    def register(username, email, password):

        connection = AuthService.get_db_connection()

        # Check if email already exists
        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:
            connection.close()
            return None

        # Create customer account
        cursor = connection.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password,
                is_admin
            )
            VALUES (?, ?, ?, 0)
            """,
            (
                username,
                email,
                password,
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        connection.close()

        return user