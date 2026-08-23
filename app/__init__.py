import os

from flask import Flask

from dotenv import load_dotenv

from app.routes.wishlist import wishlist_bp
from app.routes.reviews import reviews_bp
from app.routes.main import main_bp
from app.routes.admin import admin_bp
from app.routes.products import products_bp
from app.routes.cart import cart_bp
from app.routes.checkout import checkout_bp
from app.routes.orders import orders_bp
from app.routes.auth import auth_bp

from config.config import UPLOAD_FOLDER
from config.database import get_db_connection


def create_app():

    # =========================================================
    # LOAD ENVIRONMENT VARIABLES
    # =========================================================

    load_dotenv()

    # =========================================================
    # CREATE FLASK APP
    # =========================================================

    app = Flask(__name__)

    # =========================================================
    # FLASK CONFIGURATION
    # =========================================================

    # .env mein key ho to use karega.
    # Agar nahi hai to ye default key use hogi.
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "dx-fragrance-secret-key-2026"
    )

    app.secret_key = app.config["SECRET_KEY"]

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # =========================================================
    # REGISTER BLUEPRINTS
    # =========================================================

    app.register_blueprint(wishlist_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)

    # =========================================================
    # GLOBAL STORE SETTINGS
    # =========================================================

    @app.context_processor
    def inject_store_settings():

        connection = None

        try:

            connection = get_db_connection()

            # Existing database ke columns use karenge
            store_settings = connection.execute(
                """
                SELECT
                    id,
                    store_name,
                    store_email,
                    store_phone,
                    store_address,
                    whatsapp,
                    instagram,
                    facebook,
                    youtube
                FROM store_settings
                WHERE id = 1
                """
            ).fetchone()

            # Agar row nahi hai to default row bana do
            if store_settings is None:

                connection.execute(
                    """
                    INSERT INTO store_settings
                    (
                        id,
                        store_name,
                        store_email,
                        store_phone,
                        store_address,
                        whatsapp,
                        instagram,
                        facebook,
                        youtube
                    )
                    VALUES
                    (
                        1,
                        'DX Fragrance',
                        '',
                        '',
                        '',
                        '',
                        '',
                        ''
                    )
                    """
                )

                connection.commit()

                store_settings = connection.execute(
                    """
                    SELECT
                        id,
                        store_name,
                        store_email,
                        store_phone,
                        store_address,
                        whatsapp,
                        instagram,
                        facebook,
                        youtube
                    FROM store_settings
                    WHERE id = 1
                    """
                ).fetchone()

            # -------------------------------------------------
            # Footer ke liye address naam se bhi available hoga
            # -------------------------------------------------

            if store_settings:

                store_settings = dict(store_settings)

                store_settings["address"] = (
                    store_settings.get("store_address") or ""
                )

            return {
                "store_settings": store_settings
            }

        except Exception as error:

            print(
                "Store settings loading error:",
                error
            )

            return {
                "store_settings": None
            }

        finally:

            if connection:
                connection.close()
# Error logging enable karne ke liye ye add kar do
    import logging
    app.logger.setLevel(logging.DEBUG)
    # =========================================================
    # RETURN APP
    # =========================================================

    return app