from config.database import get_db_connection


class CustomerService:

    @staticmethod
    def get_all_customers():

        connection = get_db_connection()

        try:
            # Make sure phone column exists
            columns = connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """
            ).fetchall()

            column_names = [
                column["name"]
                for column in columns
            ]

            if "phone" not in column_names:
                connection.execute(
                    "ALTER TABLE users ADD COLUMN phone TEXT"
                )
                connection.commit()

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

                WHERE users.is_admin = 0

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

        finally:
            connection.close()


    @staticmethod
    def get_customer(customer_id):

        connection = get_db_connection()

        try:
            columns = connection.execute(
                "PRAGMA table_info(users)"
            ).fetchall()

            column_names = [
                column["name"]
                for column in columns
            ]

            if "phone" not in column_names:
                connection.execute(
                    "ALTER TABLE users ADD COLUMN phone TEXT"
                )
                connection.commit()

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
                  AND users.is_admin = 0

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

        finally:
            connection.close()