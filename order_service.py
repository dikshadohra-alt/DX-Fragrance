from config.database import get_db_connection


class OrderService:

    # =========================================================
    # GET ALL ORDERS
    # =========================================================

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

                users.username AS customer_name,
                users.email AS customer_email

            FROM orders

            LEFT JOIN users
                ON orders.user_id = users.id

            ORDER BY orders.id DESC
            """
        ).fetchall()

        connection.close()

        return orders


    # =========================================================
    # GET SINGLE ORDER
    # =========================================================

    @staticmethod
    def get_order(order_id):

        connection = get_db_connection()

        order = connection.execute(
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

                users.username AS customer_name,
                users.email AS customer_email

            FROM orders

            LEFT JOIN users
                ON orders.user_id = users.id

            WHERE orders.id = ?
            """,
            (order_id,)
        ).fetchone()


        if not order:

            connection.close()

            return None


        # =====================================================
        # GET ALL ORDER ITEMS
        # =====================================================

        items = connection.execute(
            """
            SELECT
                order_items.id,
                order_items.order_id,
                order_items.product_id,
                order_items.quantity,
                order_items.price,

                products.name AS product_name,
                products.image AS product_image

            FROM order_items

            LEFT JOIN products
                ON order_items.product_id = products.id

            WHERE order_items.order_id = ?

            ORDER BY order_items.id ASC
            """,
            (order_id,)
        ).fetchall()


        connection.close()


        # =====================================================
        # CONVERT SQLITE ROW TO DICTIONARY
        # =====================================================

        order_data = dict(order)


        # =====================================================
        # ADD ORDER ITEMS
        # =====================================================

        order_data["items"] = items


        # =====================================================
        # FIRST PRODUCT
        #
        # These values keep compatibility with the existing
        # admin order detail page.
        # =====================================================

        if items:

            first_item = items[0]


            order_data["product_name"] = (
                first_item["product_name"]
                if first_item["product_name"]
                else "Product"
            )


            order_data["product_image"] = (
                first_item["product_image"]
                if first_item["product_image"]
                else None
            )


            order_data["quantity"] = (
                first_item["quantity"]
                if first_item["quantity"]
                else 1
            )


            order_data["price"] = (
                first_item["price"]
                if first_item["price"] is not None
                else 0
            )


        else:

            order_data["product_name"] = "No Product"

            order_data["product_image"] = None

            order_data["quantity"] = 0

            order_data["price"] = 0


        # =====================================================
        # CUSTOMER INFORMATION
        #
        # Use shipping information from the actual order.
        # =====================================================

        order_data["customer_name"] = (
            order_data.get("shipping_name")
            or order_data.get("customer_name")
            or "Customer"
        )


        order_data["customer_phone"] = (
            order_data.get("shipping_phone")
            or "Not provided"
        )


        order_data["customer_address"] = (
            order_data.get("shipping_address")
            or "Not provided"
        )


        order_data["customer_email"] = (
            order_data.get("customer_email")
            or "Not available"
        )


        # =====================================================
        # ORDER DATE
        # =====================================================

        order_data["date"] = (
            order_data.get("created_at")
            or "Not available"
        )


        return order_data


    # =========================================================
    # UPDATE ORDER STATUS
    # =========================================================

    @staticmethod
    def update_status(order_id, status):

        allowed_statuses = [
            "pending",
            "confirmed",
            "shipped",
            "delivered",
            "cancelled"
        ]


        status = str(status).lower().strip()


        if status not in allowed_statuses:

            return False


        connection = get_db_connection()


        try:

            cursor = connection.execute(
                """
                UPDATE orders

                SET status = ?

                WHERE id = ?
                """,
                (
                    status,
                    order_id
                )
            )


            connection.commit()


            return cursor.rowcount > 0


        except Exception:

            connection.rollback()

            return False


        finally:

            connection.close()


    # =========================================================
    # DELETE ORDER
    # =========================================================

    @staticmethod
    def delete_order(order_id):

        connection = get_db_connection()


        try:

            # -------------------------------------------------
            # DELETE ORDER ITEMS FIRST
            # -------------------------------------------------

            connection.execute(
                """
                DELETE FROM order_items

                WHERE order_id = ?
                """,
                (order_id,)
            )


            # -------------------------------------------------
            # DELETE MAIN ORDER
            # -------------------------------------------------

            cursor = connection.execute(
                """
                DELETE FROM orders

                WHERE id = ?
                """,
                (order_id,)
            )


            connection.commit()


            return cursor.rowcount > 0


        except Exception:

            connection.rollback()

            return False


        finally:

            connection.close()