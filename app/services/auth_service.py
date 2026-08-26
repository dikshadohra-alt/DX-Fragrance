from config.database import get_db_connection, DATABASE_URL


class AuthService:

    @staticmethod
    def get_db_connection():

        connection = get_db_connection()

        # USERS TABLE
        if DATABASE_URL:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE
                )
                """
            )

        else:

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

        connection.commit()

        # -------------------------------------------------
        # DEFAULT ADMIN
        # -------------------------------------------------

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
                (
                    username,
                    email,
                    password,
                    is_admin
                )
                VALUES (?, ?, ?, 1)
                """,
                (
                    "Admin",
                    "admin@dxfragrance.com",
                    "DXAdmin@2026"
                )
            )

        else:

            connection.execute(
                """
                UPDATE users
                SET
                    password = ?,
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


    # =====================================================
    # LOGIN
    # =====================================================

    @staticmethod
    def login(email, password):

        connection = AuthService.get_db_connection()

        try:

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

            return user

        finally:

            connection.close()


    # =====================================================
    # REGISTER
    # =====================================================

    @staticmethod
    def register(username, email, password):

        connection = AuthService.get_db_connection()

        try:

            existing_user = connection.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

            if existing_user:
                return None

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
                    password
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

            return user

        finally:

            connection.close()