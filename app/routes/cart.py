from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from config.database import get_db_connection

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/cart")
def cart():

    cart_items = session.get("cart", [])

    connection = get_db_connection()

    products = []

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

        if product:
            products.append({
                "product": product,
                "quantity": item["quantity"]
            })

    connection.close()

    total = sum(
        item["product"]["price"] * item["quantity"]
        for item in products
    )

    return render_template(
        "customer/cart.html",
        cart_items=products,
        total=total
    )


@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    quantity = request.form.get("quantity", 1, type=int)

    if quantity < 1:
        quantity = 1

    connection = get_db_connection()

    product = connection.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        AND status = 'active'
        """,
        (product_id,)
    ).fetchone()

    connection.close()

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products.products"))

    if product["stock"] < quantity:
        flash("Not enough stock available.", "error")
        return redirect(
            url_for(
                "products.product_detail",
                product_id=product_id
            )
        )

    cart_items = session.get("cart", [])

    found = False

    for item in cart_items:

        if item["product_id"] == product_id:

            new_quantity = item["quantity"] + quantity

            if new_quantity > product["stock"]:
                flash("Not enough stock available.", "error")
                return redirect(
                    url_for(
                        "products.product_detail",
                        product_id=product_id
                    )
                )

            item["quantity"] = new_quantity
            found = True
            break

    if not found:

        cart_items.append({
            "product_id": product_id,
            "quantity": quantity
        })

    session["cart"] = cart_items
    session.modified = True

    flash("Product added to cart!", "success")

    return redirect(url_for("cart.cart"))


@cart_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):

    cart_items = session.get("cart", [])

    cart_items = [
        item
        for item in cart_items
        if item["product_id"] != product_id
    ]

    session["cart"] = cart_items
    session.modified = True

    flash("Product removed from cart.", "success")

    return redirect(url_for("cart.cart"))


@cart_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):

    quantity = request.form.get("quantity", 1, type=int)

    cart_items = session.get("cart", [])

    connection = get_db_connection()

    product = connection.execute(
        """
        SELECT stock
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    connection.close()

    if not product:
        return redirect(url_for("cart.cart"))

    if quantity <= 0:

        cart_items = [
            item
            for item in cart_items
            if item["product_id"] != product_id
        ]

    else:

        if quantity > product["stock"]:
            flash("Not enough stock available.", "error")
            return redirect(url_for("cart.cart"))

        for item in cart_items:

            if item["product_id"] == product_id:
                item["quantity"] = quantity
                break

    session["cart"] = cart_items
    session.modified = True

    return redirect(url_for("cart.cart"))