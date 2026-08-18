from config.database import get_db_connection


class CustomerService:

    @staticmethod
    def get_all_customers():

        connection = get_db_connection()

        customers = connection.execute(
            """
            SELECT
                users.id,
                users.username,
                users.email,
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
                users.is_admin

            ORDER BY users.id DESC
            """
        ).fetchall()

        connection.close()

        return customers


    @staticmethod
    def get_customer(customer_id):

        connection = get_db_connection()

        customer = connection.execute(
            """
            SELECT
                users.id,
                users.username,
                users.email,
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
                users.is_admin
            """,
            (customer_id,)
        ).fetchone()

        connection.close()

        return customer