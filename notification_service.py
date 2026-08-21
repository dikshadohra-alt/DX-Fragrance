from config.database import get_db_connection


class NotificationService:

    @staticmethod
    def get_notifications():

        connection = get_db_connection()

        notifications = []

        # Low stock products
        low_stock_products = connection.execute(
            """
            SELECT name, stock
            FROM products
            WHERE stock <= 5
            ORDER BY stock ASC
            """
        ).fetchall()

        for product in low_stock_products:

            if product["stock"] == 0:
                notifications.append({
                    "type": "danger",
                    "message": f"❌ {product['name']} is out of stock."
                })

            else:
                notifications.append({
                    "type": "warning",
                    "message": (
                        f"⚠️ {product['name']} "
                        f"stock is low ({product['stock']} left)."
                    )
                })

        # Recent orders
        recent_orders = connection.execute(
            """
            SELECT id, status
            FROM orders
            ORDER BY id DESC
            LIMIT 5
            """
        ).fetchall()

        for order in recent_orders:

            if order["status"] == "pending":

                notifications.append({
                    "type": "order",
                    "message": (
                        f"🛒 New order #{order['id']} received."
                    )
                })

            elif order["status"] == "delivered":

                notifications.append({
                    "type": "success",
                    "message": (
                        f"📦 Order #{order['id']} delivered."
                    )
                })

        connection.close()

        return notifications