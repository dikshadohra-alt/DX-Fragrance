from config.database import get_db_connection, DATABASE_URL


class CustomerService:

    # =========================================================
    # GET ALL CUSTOMERS
    # =========================================================

    @staticmethod
    def get_all_customers():

        connection = get_db_connection()

        try:

            # -------------------------------------------------
            # CHECK USERS TABLE COLUMNS
            # -------------------------------------------------

            if DATABASE_URL:

                columns = connection.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                    """
                ).fetchall()

            else:

                columns = connection.execute(
                    """
                    PRAGMA table_info(users)
                    """
                ).fetchall()


            column_names = [
                column["column_name"]
                for column in columns
            ]


            # -------------------------------------------------
            # ADD PHONE COLUMN IF MISSING
            # -------------------------------------------------

            if "phone" not in column_names:

                connection.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN phone TEXT
                    """
                )

                connection.commit()


            # -------------------------------------------------
            # GET ALL CUSTOMER USERS
            # -------------------------------------------------

            customers = connection.execute(
                """
                SELECT
                    users.id,
                    users.username,
                    users.email,
                    users.phone,
                    users.is_admin,

                    COUNT(DISTINCT orders.id) AS total_orders,

                    COALESCE(
                        SUM(orders.total_amount),
                        0
                    ) AS total_spending

                FROM users

                LEFT JOIN orders
                    ON users.id = orders.user_id

                WHERE users.is_admin = FALSE

                GROUP BY
                    users.id,
                    users.username,
                    users.email,
                    users.phone,
                    users.is_admin

                ORDER BY users.id DESC
                """
            ).fetchall()


            return customers


        except Exception as e:

            print(
                "Error fetching customers:",
                repr(e)
            )

            return []


        finally:

            connection.close()


    # =========================================================
    # GET SINGLE CUSTOMER
    # =========================================================

    @staticmethod
    def get_customer(customer_id):

        connection = get_db_connection()

        try:

            # -------------------------------------------------
            # CHECK USERS TABLE COLUMNS
            # -------------------------------------------------

            if DATABASE_URL:

                columns = connection.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                    """
                ).fetchall()

            else:

                columns = connection.execute(
                    """
                    PRAGMA table_info(users)
                    """
                ).fetchall()


            column_names = [
                column["column_name"]
                for column in columns
            ]


            # -------------------------------------------------
            # ADD PHONE COLUMN IF MISSING
            # -------------------------------------------------

            if "phone" not in column_names:

                connection.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN phone TEXT
                    """
                )

                connection.commit()


            # -------------------------------------------------
            # GET CUSTOMER
            # -------------------------------------------------

            customer = connection.execute(
                """
                SELECT
                    users.id,
                    users.username,
                    users.email,
                    users.phone,
                    users.is_admin,

                    COUNT(DISTINCT orders.id) AS total_orders,

                    COALESCE(
                        SUM(orders.total_amount),
                        0
                    ) AS total_spending

                FROM users

                LEFT JOIN orders
                    ON users.id = orders.user_id

                WHERE users.id = ?
                  AND users.is_admin = FALSE

                GROUP BY
                    users.id,
                    users.username,
                    users.email,
                    users.phone,
                    users.is_admin
                """,
                (customer_id,)
            ).fetchone()


            return customer


        except Exception as e:

            print(
                "Error fetching customer:",
                repr(e)
            )

            return None


        finally:

            connection.close()
