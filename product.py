from config.database import get_db_connection


class Product:

    @staticmethod
    def create(
        name,
        slug,
        price,
        category,
        description="",
        fragrance_notes="",
        size_ml=None,
        stock=0,
        image=None,
        status="active"
    ):
        connection = get_db_connection()

        cursor = connection.execute(
            """
            INSERT INTO products (
                name,
                slug,
                price,
                category,
                description,
                fragrance_notes,
                size_ml,
                stock,
                image,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                status
            )
        )

        connection.commit()

        product_id = cursor.lastrowid

        connection.close()

        return product_id


    @staticmethod
    def get_all(active_only=True):

        connection = get_db_connection()

        if active_only:
            products = connection.execute(
                """
                SELECT *
                FROM products
                WHERE status = 'active'
                ORDER BY created_at DESC
                """
            ).fetchall()

        else:
            products = connection.execute(
                """
                SELECT *
                FROM products
                ORDER BY created_at DESC
                """
            ).fetchall()

        connection.close()

        return products


    @staticmethod
    def get_by_id(product_id):

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
    def update(product_id, **fields):

        allowed_fields = {
            "name",
            "slug",
            "price",
            "category",
            "description",
            "fragrance_notes",
            "size_ml",
            "stock",
            "image",
            "status"
        }

        updates = {
            key: value
            for key, value in fields.items()
            if key in allowed_fields
        }

        if not updates:
            return False

        set_clause = ", ".join(
            f"{key} = ?"
            for key in updates
        )

        values = list(updates.values())
        values.append(product_id)

        connection = get_db_connection()

        connection.execute(
            f"""
            UPDATE products
            SET {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            values
        )

        connection.commit()

        connection.close()

        return True


    @staticmethod
    def delete(product_id):

        connection = get_db_connection()

        connection.execute(
            """
            DELETE FROM products
            WHERE id = ?
            """,
            (product_id,)
        )

        connection.commit()

        connection.close()

        return True