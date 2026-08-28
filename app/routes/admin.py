from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)


from app.services.admin_service import AdminService
from app.services.notification_service import NotificationService
from app.services.sales_service import SalesService
from app.services.inventory_service import InventoryService
from app.services.order_service import OrderService
from app.services.customer_service import CustomerService
from app.services.auth_service import AuthService
from app.services.product_service import ProductService

import os

from werkzeug.utils import secure_filename
from config.config import ALLOWED_IMAGE_EXTENSIONS


# =========================================================
# ADMIN BLUEPRINT
# =========================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# =========================================================
# ADMIN LOGIN
# =========================================================

@admin_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        user = AuthService.login(
            email,
            password
        )


        if user and user["is_admin"] == 1:

            session["admin_id"] = user["id"]

            session["admin_name"] = user["username"]

            return redirect(
                url_for("admin.dashboard")
            )


        flash(
            "Invalid admin email or password.",
            "error"
        )


    return render_template(
        "admin/login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_bp.route("/")
def dashboard():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    # -----------------------------------------------------
    # VERIFY ADMIN
    # -----------------------------------------------------

    connection = AuthService.get_db_connection()


    admin = connection.execute(
        """
        SELECT
            id,
            is_admin

        FROM users

        WHERE id = ?
        """,
        (
            session["admin_id"],
        )
    ).fetchone()


    connection.close()


    # -----------------------------------------------------
    # NOT AN ADMIN
    # -----------------------------------------------------

    if not admin or int(admin["is_admin"]) != 1:

        session.pop(
            "admin_id",
            None
        )

        session.pop(
            "admin_name",
            None
        )

        return redirect(
            url_for("main.home")
        )


    products = ProductService.get_all_products()


    return render_template(
        "admin/dashboard.html",
        products=products
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@admin_bp.route("/logout")
def logout():

    session.pop(
        "admin_id",
        None
    )

    session.pop(
        "admin_name",
        None
    )


    return redirect(
        url_for("admin.login")
    )


# =========================================================
# ADD PRODUCT
# =========================================================

@admin_bp.route(
    "/products/add",
    methods=["GET", "POST"]
)
def add_product():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()


        price = request.form.get(
            "price",
            ""
        ).strip()


        category = request.form.get(
            "category",
            ""
        ).strip()


        size_ml = request.form.get(
            "size_ml",
            ""
        ).strip()


        stock = request.form.get(
            "stock",
            ""
        ).strip()


        fragrance_notes = request.form.get(
            "fragrance_notes",
            ""
        ).strip()


        description = request.form.get(
            "description",
            ""
        ).strip()


        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        image = request.files.get(
            "image"
        )


        image_filename = None


        if image and image.filename:

            extension = image.filename.rsplit(
                ".",
                1
            )[-1].lower()


            if extension not in ALLOWED_IMAGE_EXTENSIONS:

                flash(
                    "Only JPG, JPEG, PNG and WEBP images are allowed.",
                    "error"
                )


                return render_template(
                    "admin/add_product.html"
                )


            image_filename = secure_filename(
                image.filename
            )


            upload_folder = current_app.config[
                "UPLOAD_FOLDER"
            ]


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            image.save(
                os.path.join(
                    upload_folder,
                    image_filename
                )
            )


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not name or not price or not category:

            flash(
                "Please fill all required fields.",
                "error"
            )


            return render_template(
                "admin/add_product.html"
            )


        slug = name.lower().replace(
            " ",
            "-"
        )


        try:

            product_id = ProductService.create_product(

                name=name,

                slug=slug,

                price=float(price),

                category=category,

                description=description,

                fragrance_notes=fragrance_notes,

                size_ml=int(size_ml)
                if size_ml
                else None,

                stock=int(stock)
                if stock
                else 0,

                image=image_filename
            )


            flash(
                "Perfume added successfully!",
                "success"
            )


            return redirect(
                url_for("admin.dashboard")
            )


        except Exception as error:

            flash(
                f"Error adding perfume: {error}",
                "error"
            )


    return render_template(
        "admin/add_product.html"
    )


# =========================================================
# ADMIN PRODUCTS
# =========================================================

@admin_bp.route("/products")
def products():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    products = ProductService.get_all_products()


    return render_template(
        "admin/products.html",
        products=products
    )


# =========================================================
# EDIT PRODUCT
# =========================================================

@admin_bp.route(
    "/products/edit/<int:product_id>",
    methods=["GET", "POST"]
)
def edit_product(product_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    product = ProductService.get_product(
        product_id
    )


    if not product:

        flash(
            "Product not found.",
            "error"
        )


        return redirect(
            url_for("admin.dashboard")
        )


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()


        price = request.form.get(
            "price",
            ""
        ).strip()


        category = request.form.get(
            "category",
            ""
        ).strip()


        size_ml = request.form.get(
            "size_ml",
            ""
        ).strip()


        stock = request.form.get(
            "stock",
            ""
        ).strip()


        fragrance_notes = request.form.get(
            "fragrance_notes",
            ""
        ).strip()


        description = request.form.get(
            "description",
            ""
        ).strip()


        if not name or not price or not category:

            flash(
                "Please fill all required fields.",
                "error"
            )


            return render_template(
                "admin/edit_product.html",
                product=product
            )


        # -------------------------------------------------
        # IMAGE UPDATE
        # -------------------------------------------------

        image_filename = product["image"]


        image = request.files.get(
            "image"
        )


        if image and image.filename:

            extension = image.filename.rsplit(
                ".",
                1
            )[-1].lower()


            if extension not in ALLOWED_IMAGE_EXTENSIONS:

                flash(
                    "Only JPG, JPEG, PNG and WEBP images are allowed.",
                    "error"
                )


                return render_template(
                    "admin/edit_product.html",
                    product=product
                )


            image_filename = secure_filename(
                image.filename
            )


            upload_folder = current_app.config[
                "UPLOAD_FOLDER"
            ]


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            image.save(
                os.path.join(
                    upload_folder,
                    image_filename
                )
            )


        ProductService.update_product(

            product_id=product_id,

            name=name,

            slug=name.lower().replace(
                " ",
                "-"
            ),

            price=float(price),

            category=category,

            description=description,

            fragrance_notes=fragrance_notes,

            size_ml=int(size_ml)
            if size_ml
            else None,

            stock=int(stock)
            if stock
            else 0,

            image=image_filename
        )


        flash(
            "Perfume updated successfully!",
            "success"
        )


        return redirect(
            url_for("admin.dashboard")
        )


    return render_template(
        "admin/edit_product.html",
        product=product
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@admin_bp.route(
    "/products/delete/<int:product_id>",
    methods=["POST"]
)
def delete_product(product_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    product = ProductService.delete_product(
        product_id
    )


    if product:

        flash(
            "Perfume deleted successfully!",
            "success"
        )

    else:

        flash(
            "Product not found.",
            "error"
        )


    return redirect(
        url_for("admin.dashboard")
    )


# =========================================================
# ORDERS
# =========================================================

@admin_bp.route("/orders")
def orders():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    orders = OrderService.get_all_orders()


    return render_template(
        "admin/orders.html",
        orders=orders
    )


# =========================================================
# ORDER DETAILS
# =========================================================

@admin_bp.route(
    "/orders/<int:order_id>"
)
def order_detail(order_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    order = OrderService.get_order(
        order_id
    )


    if not order:

        flash(
            "Order not found.",
            "error"
        )


        return redirect(
            url_for("admin.orders")
        )


    return render_template(
        "admin/order_detail.html",
        order=order
    )


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

@admin_bp.route(
    "/orders/update/<int:order_id>",
    methods=["POST"]
)
def update_order_status(order_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    new_status = request.form.get(
        "status",
        ""
    ).strip().lower()


    # -----------------------------------------------------
    # ALLOWED STATUS VALUES
    # -----------------------------------------------------

    allowed_statuses = [
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled"
    ]


    if new_status not in allowed_statuses:

        flash(
            "Invalid order status.",
            "error"
        )


        return redirect(
            url_for(
                "admin.order_detail",
                order_id=order_id
            )
        )


    # -----------------------------------------------------
    # UPDATE THROUGH ORDER SERVICE
    # -----------------------------------------------------

    updated = OrderService.update_status(
        order_id,
        new_status
    )


    if updated:

        flash(
            f"Order #{order_id} status updated to "
            f"{new_status.capitalize()}.",
            "success"
        )

    else:

        flash(
            "Order status could not be updated.",
            "error"
        )


    return redirect(
        url_for(
            "admin.order_detail",
            order_id=order_id
        )
    )


# =========================================================
# DELETE ORDER
# =========================================================

@admin_bp.route(
    "/orders/delete/<int:order_id>",
    methods=["POST"]
)
def delete_order(order_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    deleted = OrderService.delete_order(
        order_id
    )


    if deleted:

        flash(
            f"Order #{order_id} deleted successfully.",
            "success"
        )

    else:

        flash(
            "Order could not be deleted.",
            "error"
        )


    return redirect(
        url_for("admin.orders")
    )


# =========================================================
# CUSTOMERS
# =========================================================

@admin_bp.route("/customers")
def customers():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    customers = CustomerService.get_all_customers()


    return render_template(
        "admin/customers.html",
        customers=customers
    )
# =========================================================
# CUSTOMER DETAILS
# =========================================================

@admin_bp.route("/customers/<int:customer_id>")
def customer_detail(customer_id):

    if "admin_id" not in session:
        return redirect(
            url_for("admin.login")
        )

    customer = CustomerService.get_customer(
        customer_id
    )

    if not customer:
        flash(
            "Customer not found.",
            "error"
        )

        return redirect(
            url_for("admin.customers")
        )

    # Values required by customer_detail.html
    total_spending = customer["total_spending"] or 0
    total_orders = customer["total_orders"] or 0

    return render_template(
        "admin/customer_detail.html",
        customer=customer,
        total_spending=total_spending,
        total_orders=total_orders
    )

# =========================================================
# DELETE CUSTOMER
# =========================================================

@admin_bp.route(
    "/customers/delete/<int:customer_id>",
    methods=["POST"]
)
def delete_customer(customer_id):

    if "admin_id" not in session:
        return redirect(
            url_for("admin.login")
        )

    connection = AuthService.get_db_connection()

    try:
        customer = connection.execute(
            """
            SELECT id, username
            FROM users
            WHERE id = ?
              AND is_admin = FALSE
            """,
            (customer_id,)
        ).fetchone()

        if not customer:
            flash(
                "Customer not found.",
                "error"
            )

            return redirect(
                url_for("admin.customers")
            )

        # Delete customer's order items first
        connection.execute(
            """
            DELETE FROM order_items
            WHERE order_id IN (
                SELECT id
                FROM orders
                WHERE user_id = ?
            )
            """,
            (customer_id,)
        )

        # Delete customer's orders
        connection.execute(
            """
            DELETE FROM orders
            WHERE user_id = ?
            """,
            (customer_id,)
        )

        # Delete customer
        connection.execute(
            """
            DELETE FROM users
            WHERE id = ?
              AND is_admin = FALSE
            """,
            (customer_id,)
        )

        connection.commit()

        flash(
            f"Customer {customer['username']} deleted successfully.",
            "success"
        )

    except Exception as error:

        connection.rollback()

        current_app.logger.exception(
            "Customer deletion error: %s",
            error
        )

        flash(
            "Customer could not be deleted.",
            "error"
        )

    finally:
        connection.close()

    return redirect(
        url_for("admin.customers")
    )

# =========================================================
# INVENTORY
# =========================================================

@admin_bp.route("/inventory")
def inventory():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    products = InventoryService.get_inventory()


    return render_template(
        "admin/inventory.html",
        products=products
    )


# =========================================================
# SALES
# =========================================================

@admin_bp.route("/sales")
def sales():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    sales = SalesService.get_sales_summary()


    return render_template(
        "admin/sales.html",
        sales=sales
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@admin_bp.route("/notifications")
def notifications():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    notifications = NotificationService.get_notifications()


    return render_template(
        "admin/notifications.html",
        notifications=notifications
    )


# =========================================================
# ADMIN PROFILE
# =========================================================

@admin_bp.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )

    connection = AuthService.get_db_connection()

    try:

        # -----------------------------------------------------
        # MAKE SURE PHONE COLUMN EXISTS
        # -----------------------------------------------------
        # Agar users table mein phone column nahi hai,
        # to SQLite database mein automatically create ho jayega.
        columns = connection.execute(
            """
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position
"""
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "phone" not in column_names:

            connection.execute(
                "ALTER TABLE users ADD COLUMN phone TEXT"
            )

            connection.commit()

        # -----------------------------------------------------
        # UPDATE ADMIN PROFILE
        # -----------------------------------------------------
        if request.method == "POST":

            new_username = request.form.get(
                "username",
                ""
            ).strip()

            new_email = request.form.get(
                "email",
                ""
            ).strip()

            new_phone = request.form.get(
                "phone",
                ""
            ).strip()

            # Required fields
            if not new_username or not new_email:

                flash(
                    "Name and email are required.",
                    "error"
                )

                admin = connection.execute(
                    "SELECT * FROM users WHERE id = ?",
                    (session["admin_id"],)
                ).fetchone()

                return render_template(
                    "admin/profile.html",
                    user=admin
                )

            # -------------------------------------------------
            # SAVE NAME + EMAIL + PHONE
            # -------------------------------------------------
            connection.execute(
                """
                UPDATE users
                SET
                    username = ?,
                    email = ?,
                    phone = ?
                WHERE id = ?
                """,
                (
                    new_username,
                    new_email,
                    new_phone,
                    session["admin_id"]
                )
            )

            connection.commit()

            # Update session name too
            session["admin_name"] = new_username

            flash(
                "Profile updated successfully!",
                "success"
            )

            return redirect(
                url_for("admin.profile")
            )

        # -----------------------------------------------------
        # GET CURRENT ADMIN DETAILS
        # -----------------------------------------------------
        admin = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (
                session["admin_id"],
            )
        ).fetchone()

        return render_template(
            "admin/profile.html",
            user=admin
        )

    except Exception as error:

        connection.rollback()

        current_app.logger.exception(
            "Admin profile update error: %s",
            error
        )

        flash(
            f"Profile could not be updated: {error}",
            "error"
        )

        return redirect(
            url_for("admin.profile")
        )

    finally:

        connection.close()


# =========================================================
# CHANGE PASSWORD
# =========================================================

@admin_bp.route(
    "/change-password",
    methods=["GET", "POST"]
)
def change_password():

    if "admin_id" not in session:

        return redirect(
            url_for("admin.login")
        )


    if request.method == "POST":

        new_password = request.form.get(
            "new_password",
            ""
        ).strip()


        confirm_password = request.form.get(
            "confirm_password",
            ""
        ).strip()


        # -------------------------------------------------
        # EMPTY PASSWORD
        # -------------------------------------------------

        if not new_password or not confirm_password:

            flash(
                "Please fill both password fields.",
                "error"
            )


            return render_template(
                "admin/change_password.html"
            )


        # -------------------------------------------------
        # PASSWORD MATCH
        # -------------------------------------------------

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )


            return render_template(
                "admin/change_password.html"
            )


        # -------------------------------------------------
        # PASSWORD LENGTH
        # -------------------------------------------------

        if len(new_password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )


            return render_template(
                "admin/change_password.html"
            )


        AdminService.change_password(
            session["admin_id"],
            new_password
        )


        flash(
            "Password changed successfully!",
            "success"
        )


        return redirect(
            url_for("admin.profile")
        )


    return render_template(
        "admin/change_password.html"
    )


# =========================================================
# SETTINGS
# =========================================================

@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    connection = AuthService.get_db_connection()

    try:

        # =====================================================
        # STORE SETTINGS TABLE
        # =====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS store_settings (
                id INTEGER PRIMARY KEY,
                store_name TEXT DEFAULT 'DX Fragrance',
                store_email TEXT DEFAULT '',
                store_phone TEXT DEFAULT '',
                store_address TEXT DEFAULT '',
                instagram TEXT DEFAULT '',
                facebook TEXT DEFAULT '',
                youtube TEXT DEFAULT '',
                whatsapp TEXT DEFAULT '',
                shipping_charge REAL DEFAULT 0,
                free_shipping_threshold REAL DEFAULT 999,
                store_online INTEGER DEFAULT 1
            )
            """
        )

        connection.commit()


        # =====================================================
        # GET STORE SETTINGS COLUMNS
        # =====================================================

        database_url = (
            os.environ.get("DATABASE_URL")
            or current_app.config.get("DATABASE_URL")
            or ""
        )

        if database_url:

            columns = connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'store_settings'
                ORDER BY ordinal_position
                """
            ).fetchall()

        else:

            columns = connection.execute(
                """
                PRAGMA table_info(store_settings)
                """
            ).fetchall()


        column_names = [
            column["name"]
            for column in columns
        ]


        # =====================================================
        # ADD MISSING STORE COLUMNS
        # =====================================================

        required_columns = {
            "shipping_charge": "REAL DEFAULT 0",
            "free_shipping_threshold": "REAL DEFAULT 999",
            "store_online": "INTEGER DEFAULT 1"
        }


        for column_name, column_type in required_columns.items():

            if column_name not in column_names:

                connection.execute(
                    f"""
                    ALTER TABLE store_settings
                    ADD COLUMN {column_name} {column_type}
                    """
                )


        connection.commit()


        # =====================================================
        # CREATE DEFAULT STORE SETTINGS
        # =====================================================

        existing_store = connection.execute(
            """
            SELECT id
            FROM store_settings
            WHERE id = 1
            """
        ).fetchone()


        if not existing_store:

            connection.execute(
                """
                INSERT INTO store_settings (
                    id,
                    store_name,
                    store_email,
                    store_phone,
                    store_address,
                    instagram,
                    facebook,
                    youtube,
                    whatsapp,
                    shipping_charge,
                    free_shipping_threshold,
                    store_online
                )
                VALUES (
                    1,
                    'DX Fragrance',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    0,
                    999,
                    1
                )
                """
            )

            connection.commit()


        # =====================================================
        # PAYMENT SETTINGS TABLE
        # =====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_settings (
                id INTEGER PRIMARY KEY,
                cod_enabled INTEGER NOT NULL DEFAULT 1,
                online_payment_enabled INTEGER NOT NULL DEFAULT 0,
                upi_enabled INTEGER NOT NULL DEFAULT 1,
                cards_enabled INTEGER NOT NULL DEFAULT 1,
                netbanking_enabled INTEGER NOT NULL DEFAULT 1,
                razorpay_enabled INTEGER NOT NULL DEFAULT 0,
                upi_id TEXT DEFAULT '',
                upi_qr TEXT DEFAULT ''
            )
            """
        )

        connection.commit()


        # =====================================================
        # CREATE DEFAULT PAYMENT SETTINGS
        # =====================================================

        existing_payment = connection.execute(
            """
            SELECT id
            FROM payment_settings
            WHERE id = 1
            """
        ).fetchone()


        if not existing_payment:

            connection.execute(
                """
                INSERT INTO payment_settings (
                    id,
                    cod_enabled,
                    online_payment_enabled,
                    upi_enabled,
                    cards_enabled,
                    netbanking_enabled,
                    razorpay_enabled,
                    upi_id,
                    upi_qr
                )
                VALUES (
                    1,
                    1,
                    0,
                    1,
                    1,
                    1,
                    0,
                    '',
                    ''
                )
                """
            )

            connection.commit()


        # =====================================================
        # SAVE SETTINGS
        # =====================================================

        if request.method == "POST":

            action = request.form.get(
                "action",
                ""
            ).strip()


            # =================================================
            # STORE INFORMATION
            # =================================================

            if action == "store_info":

                store_name = request.form.get(
                    "store_name",
                    ""
                ).strip()

                store_email = request.form.get(
                    "store_email",
                    ""
                ).strip()

                store_phone = request.form.get(
                    "store_phone",
                    ""
                ).strip()

                store_address = request.form.get(
                    "store_address",
                    ""
                ).strip()


                connection.execute(
                    """
                    UPDATE store_settings
                    SET
                        store_name = ?,
                        store_email = ?,
                        store_phone = ?,
                        store_address = ?
                    WHERE id = 1
                    """,
                    (
                        store_name,
                        store_email,
                        store_phone,
                        store_address
                    )
                )


                connection.commit()


                flash(
                    "Store information saved successfully.",
                    "success"
                )


            # =================================================
            # SOCIAL LINKS
            # =================================================

            elif action == "social_links":

                instagram = request.form.get(
                    "instagram",
                    ""
                ).strip()

                facebook = request.form.get(
                    "facebook",
                    ""
                ).strip()

                youtube = request.form.get(
                    "youtube",
                    ""
                ).strip()

                whatsapp = request.form.get(
                    "whatsapp",
                    ""
                ).strip()


                connection.execute(
                    """
                    UPDATE store_settings
                    SET
                        instagram = ?,
                        facebook = ?,
                        youtube = ?,
                        whatsapp = ?
                    WHERE id = 1
                    """,
                    (
                        instagram,
                        facebook,
                        youtube,
                        whatsapp
                    )
                )


                connection.commit()


                flash(
                    "Social links saved successfully.",
                    "success"
                )


            # =================================================
            # SHIPPING
            # =================================================

            elif action == "shipping":

                try:

                    shipping_charge = float(
                        request.form.get(
                            "shipping_charge",
                            "0"
                        ).strip()
                    )

                    free_shipping_threshold = float(
                        request.form.get(
                            "free_shipping_threshold",
                            "999"
                        ).strip()
                    )

                except ValueError:

                    flash(
                        "Please enter valid shipping amounts.",
                        "error"
                    )

                else:

                    if (
                        shipping_charge < 0
                        or free_shipping_threshold < 0
                    ):

                        flash(
                            "Shipping amounts cannot be negative.",
                            "error"
                        )

                    else:

                        connection.execute(
                            """
                            UPDATE store_settings
                            SET
                                shipping_charge = ?,
                                free_shipping_threshold = ?
                            WHERE id = 1
                            """,
                            (
                                shipping_charge,
                                free_shipping_threshold
                            )
                        )


                        connection.commit()


                        flash(
                            "Shipping settings saved successfully.",
                            "success"
                        )


            # =================================================
            # STORE STATUS
            # =================================================

            elif action == "store_status":

                store_online = (
                    1
                    if request.form.get(
                        "store_online"
                    ) == "on"
                    else 0
                )


                connection.execute(
                    """
                    UPDATE store_settings
                    SET store_online = ?
                    WHERE id = 1
                    """,
                    (store_online,)
                )


                connection.commit()


                if store_online:

                    flash(
                        "Store is now ONLINE. Customers can place orders.",
                        "success"
                    )

                else:

                    flash(
                        "Store is now OFFLINE. Customers cannot place new orders.",
                        "success"
                    )


            # =================================================
            # PAYMENT SETTINGS
            # =================================================

            elif action in (
                "payment_settings",
                "payment"
            ):

                cod_enabled = (
                    1
                    if request.form.get(
                        "cod_enabled"
                    ) == "on"
                    else 0
                )


                online_payment_enabled = (
                    1
                    if request.form.get(
                        "online_payment_enabled",
                        request.form.get(
                            "online_payment"
                        )
                    ) == "on"
                    else 0
                )


                upi_enabled = (
                    1
                    if request.form.get(
                        "upi_enabled"
                    ) == "on"
                    else 0
                )


                cards_enabled = (
                    1
                    if request.form.get(
                        "cards_enabled"
                    ) == "on"
                    else 0
                )


                netbanking_enabled = (
                    1
                    if request.form.get(
                        "netbanking_enabled"
                    ) == "on"
                    else 0
                )


                razorpay_enabled = (
                    1
                    if request.form.get(
                        "razorpay_enabled"
                    ) == "on"
                    else 0
                )


                upi_id = request.form.get(
                    "upi_id",
                    ""
                ).strip()


                if upi_enabled and not upi_id:

                    flash(
                        "Please enter your UPI ID when UPI is enabled.",
                        "error"
                    )

                else:

                    qr_image = request.files.get(
                        "upi_qr"
                    )

                    qr_filename = None


                    if (
                        qr_image
                        and qr_image.filename
                    ):

                        extension = (
                            qr_image.filename
                            .rsplit(".", 1)[-1]
                            .lower()
                        )


                        if extension not in {
                            "png",
                            "jpg",
                            "jpeg",
                            "webp"
                        }:

                            flash(
                                "UPI QR must be PNG, JPG, JPEG or WEBP.",
                                "error"
                            )

                        else:

                            qr_filename = secure_filename(
                                qr_image.filename
                            )


                            _, ext = os.path.splitext(
                                qr_filename
                            )


                            qr_filename = (
                                f"upi_qr_"
                                f"{session['admin_id']}"
                                f"{ext.lower()}"
                            )


                            upload_folder = current_app.config[
                                "UPLOAD_FOLDER"
                            ]


                            os.makedirs(
                                upload_folder,
                                exist_ok=True
                            )


                            qr_image.save(
                                os.path.join(
                                    upload_folder,
                                    qr_filename
                                )
                            )


                    # -----------------------------------------
                    # KEEP OLD QR
                    # -----------------------------------------

                    if not qr_filename:

                        current_payment = connection.execute(
                            """
                            SELECT upi_qr
                            FROM payment_settings
                            WHERE id = 1
                            """
                        ).fetchone()


                        qr_filename = (
                            current_payment["upi_qr"]
                            if current_payment
                            else ""
                        )


                    # -----------------------------------------
                    # SAVE PAYMENT SETTINGS
                    # -----------------------------------------

                    connection.execute(
                        """
                        UPDATE payment_settings
                        SET
                            cod_enabled = ?,
                            online_payment_enabled = ?,
                            upi_enabled = ?,
                            cards_enabled = ?,
                            netbanking_enabled = ?,
                            razorpay_enabled = ?,
                            upi_id = ?,
                            upi_qr = ?
                        WHERE id = 1
                        """,
                        (
                            cod_enabled,
                            online_payment_enabled,
                            upi_enabled,
                            cards_enabled,
                            netbanking_enabled,
                            razorpay_enabled,
                            upi_id,
                            qr_filename or ""
                        )
                    )


                    connection.commit()


                    flash(
                        "Payment settings saved successfully.",
                        "success"
                    )


            else:

                flash(
                    "Unknown settings action.",
                    "error"
                )


            return redirect(
                url_for("admin.settings")
            )


        # =====================================================
        # LOAD STORE SETTINGS
        # =====================================================

        store_settings = connection.execute(
            """
            SELECT *
            FROM store_settings
            WHERE id = 1
            """
        ).fetchone()


        # =====================================================
        # LOAD PAYMENT SETTINGS
        # =====================================================

        payment_settings = connection.execute(
            """
            SELECT *
            FROM payment_settings
            WHERE id = 1
            """
        ).fetchone()


        return render_template(
            "admin/settings.html",
            settings=payment_settings,
            store_settings=store_settings,
            payment_settings=payment_settings
        )


    except Exception as error:

        connection.rollback()

        current_app.logger.exception(
            "Admin settings error: %s",
            error
        )

        flash(
            "Settings could not be loaded. Please check the server logs.",
            "error"
        )

        # IMPORTANT:
        # Do NOT redirect back to /admin/settings here.
        # That creates an infinite redirect loop.

        return redirect(
            url_for("admin.dashboard")
        )


    finally:

        connection.close()