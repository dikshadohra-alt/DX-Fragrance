from config.database import get_db_connection


class ReviewService:

    @staticmethod
    def get_product_reviews(product_id):

        connection = get_db_connection()

        reviews = connection.execute(
            """
            SELECT
                reviews.id,
                reviews.rating,
                reviews.comment,
                reviews.review_image,
                reviews.created_at,
                users.username AS customer_name
            FROM reviews
            JOIN users
                ON reviews.user_id = users.id
            WHERE reviews.product_id = ?
            ORDER BY reviews.id DESC
            """,
            (product_id,)
        ).fetchall()

        connection.close()

        return reviews


    @staticmethod
    def add_review(
        user_id,
        product_id,
        rating,
        review_text,
        review_image=None
    ):

        connection = get_db_connection()


        # ====================================================
        # CHECK WHETHER CUSTOMER PURCHASED THIS PRODUCT
        # ====================================================

        purchased = connection.execute(
            """
            SELECT order_items.id
            FROM order_items
            JOIN orders
                ON order_items.order_id = orders.id
            WHERE orders.user_id = ?
            AND order_items.product_id = ?
            LIMIT 1
            """,
            (
                user_id,
                product_id
            )
        ).fetchone()


        if not purchased:

            connection.close()

            return (
                False,
                "You can review only products you have purchased."
            )


        # ====================================================
        # PREVENT DUPLICATE REVIEW
        # ====================================================

        existing = connection.execute(
            """
            SELECT id
            FROM reviews
            WHERE user_id = ?
            AND product_id = ?
            """,
            (
                user_id,
                product_id
            )
        ).fetchone()


        if existing:

            connection.close()

            return (
                False,
                "You have already reviewed this product."
            )


        # ====================================================
        # ADD REVIEW
        # ====================================================

        connection.execute(
            """
            INSERT INTO reviews
            (
                user_id,
                product_id,
                rating,
                comment,
                review_image
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                product_id,
                rating,
                review_text,
                review_image
            )
        )


        connection.commit()

        connection.close()


        return (
            True,
            "Review submitted successfully!"
        )


class ReviewService:
    @staticmethod
    def get_all_reviews():
        try:
            connection = get_db_connection()
            reviews = connection.execute(
                """
                SELECT r.*, u.username, p.name as product_name 
                FROM reviews r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN products p ON r.product_id = p.id
                ORDER BY r.created_at DESC
                """
            ).fetchall()
            connection.close()
            return reviews
        except Exception as e:
            print("Error fetching reviews (safe fallback):", e)
            return []

    @staticmethod
    def delete_review(review_id):

        connection = get_db_connection()

        connection.execute(
            """
            DELETE FROM reviews
            WHERE id = ?
            """,
            (review_id,)
        )

        connection.commit()

        connection.close()

        return True