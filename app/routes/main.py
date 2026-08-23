from multiprocessing import connection

from flask import Blueprint, render_template, session
from config.database import get_db_connection


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():

    connection = get_db_connection()

    # Get all products
    # Sahi tarika (Cursor ka use karke):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Get customer's wishlist
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
            wishlist_product_ids = {row["product_id"] for row in wishlist_rows}
        except Exception as e:
            print("Wishlist fetch error:", e)
            wishlist_product_ids = set()

    connection.close()

    return render_template(
        "customer/home.html",
        products=products,
        wishlist_product_ids=wishlist_product_ids
    )