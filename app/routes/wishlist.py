from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    flash,
    request
)

from config.database import get_db_connection


wishlist_bp = Blueprint("wishlist", __name__)


# ============================================================
# VIEW WISHLIST
# ============================================================

@wishlist_bp.route("/wishlist")
def wishlist():

    if "user_id" not in session:

        flash(
            "Please login to view your wishlist.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    connection = get_db_connection()

    wishlist_items = connection.execute(
        """
        SELECT
            wishlist.id AS wishlist_id,
            products.id AS product_id,
            products.name,
            products.price,
            products.image,
            products.category,
            products.stock
        FROM wishlist
        JOIN products
            ON wishlist.product_id = products.id
        WHERE wishlist.user_id = ?
        ORDER BY wishlist.id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "customer/wishlist.html",
        wishlist_items=wishlist_items
    )


# ============================================================
# ADD TO WISHLIST
# ============================================================

@wishlist_bp.route(
    "/wishlist/add/<int:product_id>",
    methods=["POST"]
)
def add_to_wishlist(product_id):

    if "user_id" not in session:

        flash(
            "Please login to add products to wishlist.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    connection = get_db_connection()

    product = connection.execute(
        """
        SELECT id
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if not product:

        connection.close()

        flash(
            "Product not found.",
            "error"
        )

        return redirect(
            url_for("products.products")
        )

    existing = connection.execute(
        """
        SELECT id
        FROM wishlist
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            session["user_id"],
            product_id
        )
    ).fetchone()

    if not existing:

        connection.execute(
            """
            INSERT INTO wishlist
            (
                user_id,
                product_id
            )
            VALUES (?, ?)
            """,
            (
                session["user_id"],
                product_id
            )
        )

        connection.commit()

    connection.close()

    return redirect(
        request.referrer
        or url_for(
            "products.product_detail",
            product_id=product_id
        )
    )


# ============================================================
# REMOVE FROM WISHLIST USING WISHLIST ID
# ============================================================

@wishlist_bp.route(
    "/wishlist/remove/<int:wishlist_id>",
    methods=["POST"]
)
def remove_from_wishlist(wishlist_id):

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM wishlist
        WHERE id = ?
        AND user_id = ?
        """,
        (
            wishlist_id,
            session["user_id"]
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        request.referrer
        or url_for("wishlist.wishlist")
    )


# ============================================================
# REMOVE FROM WISHLIST USING PRODUCT ID
# ============================================================

@wishlist_bp.route(
    "/wishlist/remove-product/<int:product_id>",
    methods=["POST"]
)
def remove_product_from_wishlist(product_id):

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM wishlist
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            session["user_id"],
            product_id
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        request.referrer
        or url_for("wishlist.wishlist")
    )


# ============================================================
# TOGGLE WISHLIST
# ============================================================

@wishlist_bp.route(
    "/wishlist/toggle/<int:product_id>",
    methods=["POST"]
)
def toggle_wishlist(product_id):

    if "user_id" not in session:

        flash(
            "Please login to use wishlist.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    connection = get_db_connection()

    # Check if product is already in wishlist

    existing = connection.execute(
        """
        SELECT id
        FROM wishlist
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            session["user_id"],
            product_id
        )
    ).fetchone()


    # ========================================================
    # REMOVE
    # ========================================================

    if existing:

        connection.execute(
            """
            DELETE FROM wishlist
            WHERE user_id = ?
            AND product_id = ?
            """,
            (
                session["user_id"],
                product_id
            )
        )


    # ========================================================
    # ADD
    # ========================================================

    else:

        connection.execute(
            """
            INSERT INTO wishlist
            (
                user_id,
                product_id
            )
            VALUES (?, ?)
            """,
            (
                session["user_id"],
                product_id
            )
        )


    connection.commit()
    connection.close()


    # No success flash message here.
    # Heart will change automatically on page reload.

    return redirect(
        request.referrer
        or url_for("products.products")
    )