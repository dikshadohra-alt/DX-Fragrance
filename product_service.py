from config.database import get_db_connection


class ProductService:

    @staticmethod
    def create_product(
        name,
        slug,
        price,
        category,
        description,
        fragrance_notes,
        size_ml,
        stock,
        image=None
    ):
        connection = get_db_connection()

        cursor = connection.execute(
            """
            INSERT INTO products
            (
                name,
                slug,
                price,
                category,
                description,
                fragrance_notes,
                size_ml,
                stock,
                image
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                slug,
                price,
                category,
                description,
                fragrance_notes,
                size_ml,
                stock,
                image
            )
        )

        connection.commit()

        product_id = cursor.lastrowid

        connection.close()

        return product_id


    @staticmethod
    def get_all_products():

        connection = get_db_connection()

        products = connection.execute(
            """
            SELECT *
            FROM products
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        return products

    @staticmethod
    def get_product(product_id):

        connection = get_db_connection()

        product = connection.execute(
            """
            SELECT *
            FROM products
            WHERE id = ?
            """,
            (product_id,)
        ).fetchone()

        connection.close()

        return product

    @staticmethod
    def update_product(
        product_id,
        name,
        slug,
        price,
        category,
        description,
        fragrance_notes,
        size_ml,
        stock,
        image=None
    ):

        connection = get_db_connection()

        connection.execute(
            """
            UPDATE products
            SET
                name = ?,
                slug = ?,
                price = ?,
                category = ?,
                description = ?,
                fragrance_notes = ?,
                size_ml = ?,
                stock = ?,
                image = ?
            WHERE id = ?
            """,
            (
                name,
                slug,
                price,
                category,
                description,
                fragrance_notes,
                size_ml,
                stock,
                image,
                product_id
            )
        )

        connection.commit()
        connection.close()

    @staticmethod
    def delete_product(product_id):

        connection = get_db_connection()

        product = connection.execute(
            "SELECT image FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        connection.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )

        connection.commit()

        connection.close()

        return product