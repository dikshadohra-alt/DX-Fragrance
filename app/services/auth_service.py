from config.database import get_db_connection, DATABASE_URL


class AuthService:

    # =====================================================
    # DATABASE CONNECTION + USERS TABLE + DEFAULT ADMIN
    # =====================================================

    @staticmethod
    def get_db_connection():

        connection = get_db_connection()

        # -------------------------------------------------
        # USERS TABLE
        # -------------------------------------------------

        if DATABASE_URL:

            # PostgreSQL
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

            # SQLite - Local Development
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

        # -------------------------------------------------
        # CREATE ADMIN IF NOT EXISTS
        # -------------------------------------------------

        if not admin:

            if DATABASE_URL:

                # PostgreSQL
                connection.execute(
                    """
                    INSERT INTO users
                    (
                        username,
                        email,
                        password,
                        is_admin
                    )
                    VALUES (?, ?, ?, TRUE)
                    """,
                    (
                        "Admin",
                        "admin@dxfragrance.com",
                        "DXAdmin@2026"
                    )
                )

            else:

                # SQLite
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

        # -------------------------------------------------
        # MAKE SURE ADMIN REMAINS ADMIN
        # -------------------------------------------------

        else:

            if DATABASE_URL:

                # PostgreSQL
                connection.execute(
                    """
                    UPDATE users
                    SET
                        password = ?,
                        is_admin = TRUE
                    WHERE email = ?
                    """,
                    (
                        "DXAdmin@2026",
                        "admin@dxfragrance.com"
                    )
                )

            else:

                # SQLite
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
    # REGISTER CUSTOMER
    # =====================================================

    @staticmethod
    def register(username, email, password):

        connection = AuthService.get_db_connection()

        try:

            # -------------------------------------------------
            # CHECK EXISTING USER
            # -------------------------------------------------

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

            # -------------------------------------------------
            # CREATE NORMAL CUSTOMER
            # -------------------------------------------------

            if DATABASE_URL:

                # PostgreSQL
                cursor = connection.execute(
                    """
                    INSERT INTO users
                    (
                        username,
                        email,
                        password,
                        is_admin
                    )
                    VALUES (?, ?, ?, FALSE)
                    RETURNING id
                    """,
                    (
                        username,
                        email,
                        password
                    )
                )

            else:

                # SQLite
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

            # -------------------------------------------------
            # GET NEW USER ID
            # -------------------------------------------------

            user_id = cursor.lastrowid

            # -------------------------------------------------
            # GET CREATED USER
            # -------------------------------------------------

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