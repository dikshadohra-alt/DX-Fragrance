import os
import hmac
import hashlib

from dotenv import load_dotenv

# IMPORTANT:
# Project root ke .env ko Razorpay keys read karne se PEHLE load karo.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(ENV_FILE, override=True)

import razorpay

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from config.database import get_db_connection


checkout_bp = Blueprint("checkout", __name__)


# =========================================================
# RAZORPAY CONFIGURATION
# =========================================================

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "").strip()
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "").strip()


razorpay_client = None


if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(
        auth=(
            RAZORPAY_KEY_ID,
            RAZORPAY_KEY_SECRET
        )
    )


print("RAZORPAY KEY ID LOADED:", bool(RAZORPAY_KEY_ID))
print("RAZORPAY SECRET LOADED:", bool(RAZORPAY_KEY_SECRET))


# =========================================================
# CHECKOUT PAGE
# =========================================================

@checkout_bp.route("/checkout", methods=["GET", "POST"])
def checkout():

    cart_items = session.get("cart", [])

    # ---------------------------------------------------------
    # EMPTY CART
    # ---------------------------------------------------------

    if not cart_items:

        flash(
            "Your cart is empty.",
            "error"
        )

        return redirect(
            url_for("cart.cart")
        )


    # ---------------------------------------------------------
    # GET PRODUCTS
    # ---------------------------------------------------------

    connection = get_db_connection()

    products = []
    total = 0


    try:

        for item in cart_items:

            product = connection.execute(
                """
                SELECT *
                FROM products
                WHERE id = ?
                AND status = 'active'
                """,
                (
                    item["product_id"],
                )
            ).fetchone()


            if not product:

                flash(
                    "One of the products is no longer available.",
                    "error"
                )

                return redirect(
                    url_for("cart.cart")
                )


            # -------------------------------------------------
            # STOCK CHECK
            # -------------------------------------------------

            if item["quantity"] > product["stock"]:

                flash(
                    f"Not enough stock for {product['name']}.",
                    "error"
                )

                return redirect(
                    url_for("cart.cart")
                )


            # -------------------------------------------------
            # ITEM TOTAL
            # -------------------------------------------------

            item_total = (
                product["price"]
                * item["quantity"]
            )

            total += item_total


            products.append({
                "product": product,
                "quantity": item["quantity"],
                "item_total": item_total
            })


    finally:

        connection.close()


    # =========================================================
    # LOGIN CHECK
    # =========================================================

    if "user_id" not in session:

        flash(
            "Please login before placing your order.",
            "error"
        )

        return redirect(
            url_for("main.home")
        )


    # =========================================================
    # POST REQUEST
    # =========================================================

    if request.method == "POST":

        # -----------------------------------------------------
        # SHIPPING DETAILS
        # -----------------------------------------------------

        shipping_name = request.form.get(
            "shipping_name",
            ""
        ).strip()


        shipping_phone = request.form.get(
            "shipping_phone",
            ""
        ).strip()


        shipping_address = request.form.get(
            "shipping_address",
            ""
        ).strip()


        # -----------------------------------------------------
        # PAYMENT METHOD
        # -----------------------------------------------------

        payment_method = request.form.get(
            "payment_method",
            "cod"
        ).strip().lower()


        # =====================================================
        # SHIPPING VALIDATION
        # =====================================================

        if (
            not shipping_name
            or not shipping_phone
            or not shipping_address
        ):

            flash(
                "Please fill all shipping details.",
                "error"
            )

            return render_template(
                "customer/checkout.html",
                products=products,
                total=total,
                razorpay_key_id=RAZORPAY_KEY_ID
            )


        # =====================================================
        # ONLINE PAYMENT
        # =====================================================

        if payment_method == "online":

            # -------------------------------------------------
            # CHECK RAZORPAY CONFIGURATION
            # -------------------------------------------------

            if not razorpay_client:

                print(
                    "RAZORPAY CONFIG ERROR:"
                    " Key ID or Key Secret is missing."
                )

                flash(
                    "Online payment is not configured yet.",
                    "error"
                )

                return render_template(
                    "customer/checkout.html",
                    products=products,
                    total=total,
                    razorpay_key_id=RAZORPAY_KEY_ID
                )


            try:

                # -------------------------------------------------
                # RAZORPAY AMOUNT
                # Razorpay amount paise mein leta hai.
                # Example: ₹1999 = 199900 paise
                # -------------------------------------------------

                amount_paise = int(
                    round(total * 100)
                )


                # -------------------------------------------------
                # CREATE RAZORPAY ORDER
                # -------------------------------------------------

                razorpay_order = razorpay_client.order.create(
                    data={
                        "amount": amount_paise,
                        "currency": "INR",
                        "receipt": (
                            f"DX-"
                            f"{session['user_id']}-"
                            f"{int(total)}"
                        ),
                        "payment_capture": 1
                    }
                )


                # -------------------------------------------------
                # STORE PENDING PAYMENT IN SESSION
                # -------------------------------------------------

                session["pending_payment"] = {

                    "razorpay_order_id": (
                        razorpay_order["id"]
                    ),

                    "shipping_name": (
                        shipping_name
                    ),

                    "shipping_phone": (
                        shipping_phone
                    ),

                    "shipping_address": (
                        shipping_address
                    ),

                    "total": total
                }


                session.modified = True


                # -------------------------------------------------
                # OPEN PAYMENT PAGE
                # -------------------------------------------------

                return render_template(
                    "customer/payment.html",

                    razorpay_key_id=(
                        RAZORPAY_KEY_ID
                    ),

                    razorpay_order_id=(
                        razorpay_order["id"]
                    ),

                    amount=amount_paise,

                    total=total,

                    shipping_name=(
                        shipping_name
                    ),

                    shipping_phone=(
                        shipping_phone
                    )
                )


            except Exception as e:

                print(
                    "RAZORPAY ORDER ERROR:",
                    repr(e)
                )

                flash(
                    f"Unable to start online payment: {e}",
                    "error"
                )

                return render_template(
                    "customer/checkout.html",
                    products=products,
                    total=total,
                    razorpay_key_id=RAZORPAY_KEY_ID
                )
            


        # =====================================================
        # CASH ON DELIVERY
        # =====================================================

        if payment_method == "cod":

            connection = get_db_connection()

            # Safety Check for order_items table
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
                """
            )
            connection.commit()


            try:

                # -------------------------------------------------
                # CREATE COD ORDER
                # -------------------------------------------------

                cursor = connection.execute(
                    """
                    INSERT INTO orders (
                        user_id,
                        total_price,
                        status,
                        shipping_name,
                        shipping_phone,
                        shipping_address
                    )
                    VALUES (
                        ?,
                        ?,
                        'pending',
                        ?,
                        ?,
                        ?
                    )
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


                # -------------------------------------------------
                # ORDER ITEMS + STOCK
                # -------------------------------------------------

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


                    # -------------------------------------------------
                    # DECREASE STOCK
                    # -------------------------------------------------

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


                # -------------------------------------------------
                # CLEAR CART
                # -------------------------------------------------

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

                print(
                    "COD ORDER ERROR:",
                    e
                )

                flash(
                    "Something went wrong while placing your order.",
                    "error"
                )


            finally:

                connection.close()


    # =========================================================
    # GET CHECKOUT PAGE
    # =========================================================

    return render_template(
        "customer/checkout.html",
        products=products,
        total=total,
        razorpay_key_id=RAZORPAY_KEY_ID
    )


# =========================================================
# PAYMENT SUCCESS
# =========================================================

@checkout_bp.route(
    "/payment/success",
    methods=["POST"]
)
def payment_success():

    # ---------------------------------------------------------
    # LOGIN CHECK
    # ---------------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login."
        }), 401


    # ---------------------------------------------------------
    # GET PAYMENT DATA
    # ---------------------------------------------------------

    data = request.get_json()


    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid payment data."
        }), 400


    razorpay_payment_id = data.get(
        "razorpay_payment_id"
    )


    razorpay_order_id = data.get(
        "razorpay_order_id"
    )


    razorpay_signature = data.get(
        "razorpay_signature"
    )


    # ---------------------------------------------------------
    # CHECK PAYMENT DETAILS
    # ---------------------------------------------------------

    if not all([
        razorpay_payment_id,
        razorpay_order_id,
        razorpay_signature
    ]):

        return jsonify({
            "success": False,
            "message": "Incomplete payment details."
        }), 400


    # =========================================================
    # VERIFY ORDER ID FROM SESSION
    # =========================================================

    pending_payment = session.get(
        "pending_payment"
    )


    if not pending_payment:

        return jsonify({
            "success": False,
            "message": "Payment session expired."
        }), 400


    server_order_id = pending_payment[
        "razorpay_order_id"
    ]


    # ---------------------------------------------------------
    # DO NOT TRUST ORDER ID FROM BROWSER
    # ---------------------------------------------------------

    if razorpay_order_id != server_order_id:

        return jsonify({
            "success": False,
            "message": "Invalid payment order."
        }), 400


    # =========================================================
    # VERIFY PAYMENT SIGNATURE
    # =========================================================

    if not RAZORPAY_KEY_SECRET:

        return jsonify({
            "success": False,
            "message": "Payment configuration error."
        }), 500


    generated_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        (
            f"{server_order_id}"
            f"|"
            f"{razorpay_payment_id}"
        ).encode(),
        hashlib.sha256
    ).hexdigest()


    if not hmac.compare_digest(
        generated_signature,
        razorpay_signature
    ):

        return jsonify({
            "success": False,
            "message": "Payment verification failed."
        }), 400


    # =========================================================
    # CREATE ACTUAL ORDER
    # =========================================================

    connection = get_db_connection()

    # Safety Check for order_items table
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """
    )
    connection.commit()


    try:

        # -----------------------------------------------------
        # GET SHIPPING DETAILS
        # -----------------------------------------------------

        shipping_name = pending_payment[
            "shipping_name"
        ]


        shipping_phone = pending_payment[
            "shipping_phone"
        ]


        shipping_address = pending_payment[
            "shipping_address"
        ]


        total = pending_payment[
            "total"
        ]


        # -----------------------------------------------------
        # CREATE ORDER
        # -----------------------------------------------------

        cursor = connection.execute(
            """
            INSERT INTO orders (
                user_id,
                total_price,
                status,
                shipping_name,
                shipping_phone,
                shipping_address
            )
            VALUES (
                ?,
                ?,
                'confirmed',
                ?,
                ?,
                ?
            )
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


        # =====================================================
        # GET CART AGAIN
        # =====================================================

        cart_items = session.get(
            "cart",
            []
        )


        # =====================================================
        # ORDER ITEMS + STOCK
        # =====================================================

        for item in cart_items:

            product = connection.execute(
                """
                SELECT *
                FROM products
                WHERE id = ?
                AND status = 'active'
                """,
                (
                    item["product_id"],
                )
            ).fetchone()


            if not product:

                raise Exception(
                    "Product no longer available."
                )


            quantity = item["quantity"]


            # -------------------------------------------------
            # STOCK CHECK
            # -------------------------------------------------

            if quantity > product["stock"]:

                raise Exception(
                    f"Not enough stock for "
                    f"{product['name']}."
                )


            # -------------------------------------------------
            # SAVE ORDER ITEM
            # -------------------------------------------------

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


            # -------------------------------------------------
            # DECREASE STOCK
            # -------------------------------------------------

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


        # -----------------------------------------------------
        # COMMIT ORDER
        # -----------------------------------------------------

        connection.commit()


        # =====================================================
        # CLEAR CART + PAYMENT SESSION
        # =====================================================

        session["cart"] = []


        session.pop(
            "pending_payment",
            None
        )


        session.modified = True


        # -----------------------------------------------------
        # SUCCESS RESPONSE
        # -----------------------------------------------------

        return jsonify({
            "success": True,
            "order_id": order_id
        })


    except Exception as e:

        connection.rollback()

        print(
            "PAYMENT ORDER ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "message": (
                "Payment received but "
                "order creation failed."
            )
        }), 500


    finally:

        connection.close()