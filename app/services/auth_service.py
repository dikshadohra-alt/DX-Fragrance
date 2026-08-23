from config.database import get_db_connection


class AuthService:

    @staticmethod
    def get_db_connection():
        return get_db_connection()

    # =========================================================
    # LOGIN
    # =========================================================

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


    # =========================================================
    # REGISTER
    # =========================================================

    @staticmethod
    def register(username, email, password):

        connection = AuthService.get_db_connection()

        try:

            # -------------------------------------------------
            # CHECK EXISTING EMAIL
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
            # CREATE CUSTOMER
            # -------------------------------------------------

            connection.execute(
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
            # GET NEW USER
            # -------------------------------------------------

            user = connection.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()


            return user

        finally:

            connection.close()