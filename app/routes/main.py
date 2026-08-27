from flask import Blueprint, render_template, session
from config.database import get_db_connection


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():

    connection = get_db_connection()

    try:

        # =====================================================
        # GET ALL PRODUCTS
        # =====================================================

        products = connection.execute(
            """
            SELECT *
            FROM products
            ORDER BY id DESC
            """
        ).fetchall()


        # =====================================================
        # GET CUSTOMER WISHLIST
        # =====================================================

        wishlist_product_ids = set()

        if session.get("user_id"):

            try:

                wishlist_rows = connection.execute(
                    """
                    SELECT product_id
                    FROM wishlist
                    WHERE user_id = ?
                    """,
                    (session["user_id"],)
                ).fetchall()

                wishlist_product_ids = {
                    row["product_id"]
                    for row in wishlist_rows
                }

            except Exception as e:

                print(
                    "Wishlist fetch error:",
                    repr(e)
                )

                wishlist_product_ids = set()


        # =====================================================
        # HOME PAGE
        # =====================================================

        return render_template(
            "customer/home.html",
            products=products,
            wishlist_product_ids=wishlist_product_ids
        )


    finally:

        connection.close()