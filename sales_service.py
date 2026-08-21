from config.database import get_db_connection


class SalesService:

    @staticmethod
    def get_sales_summary():

        connection = get_db_connection()

        today_sales = connection.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0)
            FROM orders
            WHERE status = 'delivered'
            AND DATE(created_at) = DATE('now')
            """
        ).fetchone()[0]

        monthly_sales = connection.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0)
            FROM orders
            WHERE status = 'delivered'
            AND strftime('%Y-%m', created_at)
                = strftime('%Y-%m', 'now')
            """
        ).fetchone()[0]

        total_revenue = connection.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0)
            FROM orders
            WHERE status = 'delivered'
            """
        ).fetchone()[0]

        best_seller = connection.execute(
            """
            SELECT
                products.name,
                SUM(order_items.quantity) AS total_sold
            FROM order_items
            JOIN products
                ON order_items.product_id = products.id
            JOIN orders
                ON order_items.order_id = orders.id
            WHERE orders.status = 'delivered'
            GROUP BY products.id
            ORDER BY total_sold DESC
            LIMIT 1
            """
        ).fetchone()

        connection.close()

        return {
            "today_sales": today_sales,
            "monthly_sales": monthly_sales,
            "total_revenue": total_revenue,
            "best_seller": best_seller
        }