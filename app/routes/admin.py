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

# =========================================================
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
# CUSTOMER DETAIL
# =========================================================

@admin_bp.route("/customers/<int:customer_id>")
def customer_detail(customer_id):

    if "admin_id" not in session:
        return redirect(
            url_for("admin.login")
        )

    connection = AuthService.get_db_connection()

    try:

        customer = connection.execute(
            """
            SELECT
                id,
                username,
                email,
                phone,
                is_admin
            FROM users
            WHERE id = ?
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


        orders = connection.execute(
            """
            SELECT
                id,
                total_amount,
                status,
                shipping_name,
                shipping_phone,
                shipping_address,
                created_at
            FROM orders
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (customer_id,)
        ).fetchall()


        total_orders = len(orders)


        result = connection.execute(
            """
            SELECT
                COALESCE(SUM(total_amount), 0)
            FROM orders
            WHERE user_id = ?
            AND LOWER(
                COALESCE(status, '')
            ) != 'cancelled'
            """,
            (customer_id,)
        ).fetchone()


        total_spending = result[0] if result else 0


        latest_order = connection.execute(
            """
            SELECT
                shipping_name,
                shipping_phone,
                shipping_address
            FROM orders
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (customer_id,)
        ).fetchone()


        return render_template(
            "admin/customer_detail.html",
            customer=customer,
            orders=orders,
            total_orders=total_orders,
            total_spending=total_spending,
            latest_order=latest_order
        )


    except Exception as error:

        current_app.logger.exception(
            "Customer detail error: %s",
            error
        )

        flash(
            "Unable to load customer details.",
            "error"
        )

        return redirect(
            url_for("admin.customers")
        )


    finally:

        connection.close()


# =========================================================
# INVENTORY
# =========================================================

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
            "PRAGMA table_info(users)"
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
# STORE SETTINGS
# =========================================================

@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():

    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    connection = AuthService.get_db_connection()

    try:

        # -------------------------------------------------
        # CREATE TABLE IF NOT EXISTS
        # -------------------------------------------------

        connection.execute("""
            CREATE TABLE IF NOT EXISTS store_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                store_name TEXT DEFAULT 'DX Fragrance',
                store_email TEXT DEFAULT 'admin@dxfragrance.com',
                store_phone TEXT DEFAULT '',
                store_address TEXT DEFAULT '',
                instagram TEXT DEFAULT '',
                facebook TEXT DEFAULT '',
                youtube TEXT DEFAULT '',
                whatsapp TEXT DEFAULT '',
                shipping_charge REAL DEFAULT 0,
                free_shipping_threshold REAL DEFAULT 999,
                cod_enabled INTEGER DEFAULT 1,
                online_payment INTEGER DEFAULT 0,
                store_online INTEGER DEFAULT 1,
                address TEXT DEFAULT ''
            )
        """)

        # -------------------------------------------------
        # MAKE SURE DEFAULT ROW EXISTS
        # -------------------------------------------------

        connection.execute("""
            INSERT OR IGNORE INTO store_settings (id)
            VALUES (1)
        """)

        connection.commit()

        # -------------------------------------------------
        # SAVE SETTINGS
        # -------------------------------------------------

        if request.method == "POST":

            action = request.form.get("action", "").strip()

            # =================================================
            # STORE INFORMATION
            # =================================================

            if action == "store_info":

                store_name = request.form.get(
                    "store_name", ""
                ).strip()

                store_email = request.form.get(
                    "store_email", ""
                ).strip()

                store_phone = request.form.get(
                    "store_phone", ""
                ).strip()

                store_address = request.form.get(
                    "store_address", ""
                ).strip()

                connection.execute("""
                    UPDATE store_settings
                    SET
                        store_name = ?,
                        store_email = ?,
                        store_phone = ?,
                        store_address = ?
                    WHERE id = 1
                """, (
                    store_name,
                    store_email,
                    store_phone,
                    store_address
                ))

                connection.commit()

                flash(
                    "Store information updated successfully!",
                    "success"
                )

            # =================================================
            # SOCIAL MEDIA
            # =================================================

            elif action == "social_links":

                instagram = request.form.get(
                    "instagram", ""
                ).strip()

                facebook = request.form.get(
                    "facebook", ""
                ).strip()

                youtube = request.form.get(
                    "youtube", ""
                ).strip()

                whatsapp = request.form.get(
                    "whatsapp", ""
                ).strip()

                connection.execute("""
                    UPDATE store_settings
                    SET
                        instagram = ?,
                        facebook = ?,
                        youtube = ?,
                        whatsapp = ?
                    WHERE id = 1
                """, (
                    instagram,
                    facebook,
                    youtube,
                    whatsapp
                ))

                connection.commit()

                flash(
                    "Social links updated successfully!",
                    "success"
                )

            # =================================================
            # SHIPPING SETTINGS
            # =================================================

            elif action == "shipping":

                shipping_charge = request.form.get(
                    "shipping_charge", "0"
                ).strip()

                free_shipping_threshold = request.form.get(
                    "free_shipping_threshold", "999"
                ).strip()

                try:

                    shipping_charge = float(
                        shipping_charge or 0
                    )

                    free_shipping_threshold = float(
                        free_shipping_threshold or 999
                    )

                    connection.execute("""
                        UPDATE store_settings
                        SET
                            shipping_charge = ?,
                            free_shipping_threshold = ?
                        WHERE id = 1
                    """, (
                        shipping_charge,
                        free_shipping_threshold
                    ))

                    connection.commit()

                    flash(
                        "Shipping settings updated successfully!",
                        "success"
                    )

                except (ValueError, TypeError) as error:

                    connection.rollback()

                    flash(
                        f"Invalid shipping value: {error}",
                        "error"
                    )

            # =================================================
            # OTHER SETTINGS
            # =================================================

            else:

                flash(
                    "No settings action selected.",
                    "error"
                )

            return redirect(
                url_for("admin.settings")
            )

        # -------------------------------------------------
        # LOAD CURRENT SETTINGS
        # -------------------------------------------------

        settings = connection.execute("""
            SELECT *
            FROM store_settings
            WHERE id = 1
        """).fetchone()

        return render_template(
    "admin/settings.html",
    settings=settings,
    store_settings=settings
)
    except Exception as error:

        connection.rollback()

        current_app.logger.exception(
            "Store settings error: %s",
            error
        )

        flash(
            f"Store settings could not be updated: {error}",
            "error"
        )

        return redirect(
            url_for("admin.settings")
        )

    finally:

        connection.close()