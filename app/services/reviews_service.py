from config.database import get_db_connection


class ReviewService:

    @staticmethod
    def get_product_reviews(product_id):
        try:
            connection = get_db_connection()
            reviews = connection.execute(
                """
                SELECT 
                    r.id,
                    r.rating,
                    r.comment,
                    r.created_at,
                    u.username AS customer_name
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.product_id = ?
                ORDER BY r.id DESC
                """,
                (product_id,)
            ).fetchall()
            connection.close()
            return reviews
        except Exception as e:
            print("Error fetching product reviews:", e)
            return []

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
            print("Error fetching all reviews:", e)
            return []

    @staticmethod
    def add_review(user_id, product_id, rating, review_text, review_image=None):
        try:
            connection = get_db_connection()
            
            # Add review query
            connection.execute(
                """
                INSERT INTO reviews (user_id, product_id, rating, comment)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, product_id, rating, review_text)
            )
            connection.commit()
            connection.close()
            return True, "Review submitted successfully!"
        except Exception as e:
            print("Error adding review:", e)
            return False, str(e)

    @staticmethod
    def delete_review(review_id):
        try:
            connection = get_db_connection()
            connection.execute(
                "DELETE FROM reviews WHERE id = ?",
                (review_id,)
            )
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print("Error deleting review:", e)
            return False