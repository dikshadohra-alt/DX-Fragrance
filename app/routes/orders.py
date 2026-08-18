from flask import Blueprint, render_template, session, redirect, url_for, flash
from config.database import get_db_connection


orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/orders")
def my_orders():

    if "user_id" not in session:
        flash("Please login to view your orders.", "error")
        return redirect(url_for("main.home"))

    connection = get_db_connection()

    orders = connection.execute(
        """
        SELECT *
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "customer/orders.html",
        orders=orders
    )


@orders_bp.route("/orders/<int:order_id>")
def order_detail(order_id):

    if "user_id" not in session:
        flash("Please login to view your order.", "error")
        return redirect(url_for("main.home"))

    connection = get_db_connection()

    order = connection.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
        AND user_id = ?
        """,
        (order_id, session["user_id"])
    ).fetchone()

    if not order:
        connection.close()
        flash("Order not found.", "error")
        return redirect(url_for("orders.my_orders"))

    items = connection.execute(
        """
        SELECT
            order_items.*,
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

    return render_template(
        "customer/order_detail.html",
        order=order,
        items=items
    )


@orders_bp.route("/orders/success/<int:order_id>")
def order_success(order_id):

    if "user_id" not in session:
        flash("Please login to view your order.", "error")
        return redirect(url_for("main.home"))

    connection = get_db_connection()

    order = connection.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
        AND user_id = ?
        """,
        (order_id, session["user_id"])
    ).fetchone()

    connection.close()

    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders.my_orders"))

    return render_template(
        "customer/order_success.html",
        order=order
    )