from config.database import get_db_connection


class OrderService:

    @staticmethod
    def get_all_orders():

        connection = get_db_connection()

        orders = connection.execute(
            """
            SELECT
                orders.id,
                orders.user_id,
                orders.total_amount,
                orders.status,
                orders.shipping_name,
                orders.shipping_phone,
                orders.shipping_address,
                orders.created_at,
                users.name AS customer_name,
                users.email AS customer_email
            FROM orders
            JOIN users
                ON orders.user_id = users.id
            ORDER BY orders.id DESC
            """
        ).fetchall()

        connection.close()

        return orders


    @staticmethod
    def get_order(order_id):

        connection = get_db_connection()

        order = connection.execute(
            """
            SELECT
                orders.*,
                users.name AS customer_name,
                users.email AS customer_email
            FROM orders
            JOIN users
                ON orders.user_id = users.id
            WHERE orders.id = ?
            """,
            (order_id,)
        ).fetchone()

        if not order:
            connection.close()
            return None

        items = connection.execute(
            """
            SELECT
                order_items.id,
                order_items.quantity,
                order_items.price,
                products.name AS product_name,
                products.image AS product_image
            FROM order_items
            JOIN products
                ON order_items.product_id = products.id
            WHERE order_items.order_id = ?
            """,
            (order_id,)
        ).fetchall()

        connection.close()

        return {
            "order": order,
            "items": items
        } 


    @staticmethod
    def update_status(order_id, status):

        connection = get_db_connection()

        connection.execute(
            """
            UPDATE orders
            SET status = ?
            WHERE id = ?
            """,
            (status, order_id)
        )

        connection.commit()
        connection.close()