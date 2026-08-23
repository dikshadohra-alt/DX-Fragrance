from flask import (
    Blueprint,
    render_template,
    abort,
    session,
    request
)

from config.database import get_db_connection
from app.services.reviews_service import ReviewService


products_bp = Blueprint("products", __name__)


# ============================================================
# SHOP
# ============================================================

@products_bp.route("/products")
def products():

    # --------------------------------------------------------
    # GET FILTER VALUES
    # --------------------------------------------------------

    search = request.args.get(
        "search",
        ""
    ).strip()

    selected_category = request.args.get(
        "category",
        ""
    ).strip()

    selected_sort = request.args.get(
        "sort",
        ""
    ).strip()


    connection = get_db_connection()


    # ========================================================
    # GET CATEGORIES
    # ========================================================

    category_rows = connection.execute(
        """
        SELECT DISTINCT category
        FROM products
        WHERE status = 'active'
        AND category IS NOT NULL
        AND category != ''
        ORDER BY category ASC
        """
    ).fetchall()


    categories = [
        row["category"]
        for row in category_rows
    ]


    # ========================================================
    # BUILD PRODUCT QUERY
    # ========================================================

    query = """
        SELECT *
        FROM products
        WHERE status = 'active'
    """

    params = []


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:

        query += """
            AND (
                name LIKE ?
                OR category LIKE ?
                OR description LIKE ?
                OR fragrance_notes LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])


    # --------------------------------------------------------
    # CATEGORY FILTER
    # --------------------------------------------------------

    if selected_category:

        query += """
            AND category = ?
        """

        params.append(
            selected_category
        )


    # ========================================================
    # SORT
    # ========================================================

    if selected_sort == "price_low":

        query += """
            ORDER BY price ASC
        """

    elif selected_sort == "price_high":

        query += """
            ORDER BY price DESC
        """

    elif selected_sort == "name":

        query += """
            ORDER BY name ASC
        """

    else:

        # newest/default
        query += """
            ORDER BY id DESC
        """


    # ========================================================
    # GET PRODUCTS
    # ========================================================

    products = connection.execute(
        query,
        params
    ).fetchall()


    connection.close()


    # ========================================================
    # RENDER SHOP
    # ========================================================

    return render_template(
        "customer/shop.html",
        products=products,
        categories=categories,
        search=search,
        selected_category=selected_category,
        selected_sort=selected_sort
    )


# ============================================================
# PRODUCT DETAIL
# ============================================================
@products_bp.route("/product/<product_id>")
def product_detail(product_id):

    connection = get_db_connection()

    print("PRODUCT DETAIL REQUESTED ID:", product_id)

    product = connection.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        AND status = 'active'
        """,
        (product_id,)
    ).fetchone()

    print("PRODUCT FOUND:", product)

    if not product:
        connection.close()
        abort(404)

    wishlist_added = False

    if "user_id" in session:

        wishlist = connection.execute(
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

        if wishlist:
            wishlist_added = True

    connection.close()

    reviews = ReviewService.get_product_reviews(
        product_id
    )

    return render_template(
        "customer/product.html",
        product=product,
        wishlist_added=wishlist_added,
        reviews=reviews
    )
    # ========================================================
    # GET PRODUCT
    # ========================================================
    
    print("PRODUCT DETAIL REQUESTED ID:", product_id)
    product = connection.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        AND status = 'active'
        """,
        (product_id,)
    ).fetchone()
    print("PRODUCT FOUND:", product)

    if not product:

        connection.close()

        abort(404)


    # ========================================================
    # CHECK WISHLIST
    # ========================================================

    wishlist_added = False


    if "user_id" in session:

        wishlist = connection.execute(
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


        if wishlist:

            wishlist_added = True


    connection.close()


    # ========================================================
    # GET PRODUCT REVIEWS
    # ========================================================

    reviews = ReviewService.get_product_reviews(
        product_id
    )


    # ========================================================
    # RENDER PRODUCT PAGE
    # ========================================================

    return render_template(
        "customer/product.html",
        product=product,
        wishlist_added=wishlist_added,
        reviews=reviews
    )

@products_bp.route("/products/search-suggestions")
def search_suggestions():

    search = request.args.get(
        "q",
        ""
    ).strip()

    if not search:
        return []


    connection = get_db_connection()


    rows = connection.execute(
        """
        SELECT
            id,
            name,
            category,
            price,
            image
        FROM products
        WHERE status = 'active'
        AND (
            name LIKE ?
            OR category LIKE ?
        )
        ORDER BY id DESC
        LIMIT 8
        """,
        (
            f"%{search}%",
            f"%{search}%"
        )
    ).fetchall()


    connection.close()


    return [
        {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "price": row["price"],
            "image": row["image"]
        }
        for row in rows
    ]