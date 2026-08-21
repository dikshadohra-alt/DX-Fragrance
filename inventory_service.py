from config.database import get_db_connection


class InventoryService:

    @staticmethod
    def get_inventory():

        connection = get_db_connection()

        products = connection.execute(
            """
            SELECT
                id,
                name,
                category,
                stock,
                price,
                status
            FROM products
            ORDER BY stock ASC, id DESC
            """
        ).fetchall()

        connection.close()

        return products