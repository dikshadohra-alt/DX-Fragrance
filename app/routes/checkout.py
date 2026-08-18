from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config.database import get_db_connection


checkout_bp = Blueprint("checkout", __name__)


@checkout_bp.route("/checkout", methods=["GET", "POST"])
def checkout():

    cart_items = session.get("cart", [])

    if not cart_items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart.cart"))

    connection = get_db_connection()

    products = []
    total = 0

    for item in cart_items:

        product = connection.execute(
            """
            SELECT *
            FROM products
            WHERE id = ?
            AND status = 'active'
            """,
            (item["product_id"],)
        ).fetchone()

        if not product:
            connection.close()
            flash("One of the products is no longer available.", "error")
            return redirect(url_for("cart.cart"))

        if item["quantity"] > product["stock"]:
            connection.close()
            flash(
                f"Not enough stock for {product['name']}.",
                "error"
            )
            return redirect(url_for("cart.cart"))

        item_total = product["price"] * item["quantity"]

        total += item_total

        products.append({
            "product": product,
            "quantity": item["quantity"],
            "item_total": item_total
        })

    connection.close()

    if request.method == "POST":

        if "user_id" not in session:
           flash("Please login before placing your order.", "error")
           return redirect(url_for("main.home"))

        shipping_name = request.form.get("shipping_name", "").strip()
        shipping_phone = request.form.get("shipping_phone", "").strip()
        shipping_address = request.form.get("shipping_address", "").strip()

        if not shipping_name or not shipping_phone or not shipping_address:
            flash("Please fill all shipping details.", "error")

            return render_template(
                "customer/checkout.html",
                products=products,
                total=total
            )

        connection = get_db_connection()

        try:

            # Create order
            cursor = connection.execute(
                """
                INSERT INTO orders (
                    user_id,
                    total_amount,
                    status,
                    shipping_name,
                    shipping_phone,
                    shipping_address
                )
                VALUES (?, ?, 'pending', ?, ?, ?)
                """,
                (
                    session["user_id"],
                    total,
                    shipping_name,
                    shipping_phone,
                    shipping_address
                )
            )

            order_id = cursor.lastrowid

            # Create order items + decrease stock
            for item in products:

                product = item["product"]
                quantity = item["quantity"]

                connection.execute(
                    """
                    INSERT INTO order_items (
                        order_id,
                        product_id,
                        quantity,
                        price
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        product["id"],
                        quantity,
                        product["price"]
                    )
                )

                connection.execute(
                    """
                    UPDATE products
                    SET stock = stock - ?
                    WHERE id = ?
                    """,
                    (
                        quantity,
                        product["id"]
                    )
                )

            connection.commit()

            # Empty cart after successful order
            session["cart"] = []
            session.modified = True

            flash(
                "Order placed successfully!",
                "success"
            )

            return redirect(
                url_for(
                    "orders.order_success",
                    order_id=order_id
                )
            )

        except Exception as e:

            connection.rollback()

            flash(
                "Something went wrong while placing your order.",
                "error"
            )

            print("ORDER ERROR:", e)

        finally:

            connection.close()

    return render_template(
        "customer/checkout.html",
        products=products,
        total=total
    )