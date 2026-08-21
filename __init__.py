import os
import sqlite3
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


def init_db_on_startup():
    """Ensures database and tables are automatically created on cloud/render startup if missing."""
    db_dir = os.path.join(os.getcwd(), 'database')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'dx_fragrance.db')
    
    # Agar database file nahi hai ya khali hai, toh schema.sql se tables bana do
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        schema_path = os.path.join(db_dir, 'schema.sql')
        if os.path.exists(schema_path):
            connection = sqlite3.connect(db_path)
            with open(schema_path, 'r', encoding='utf-8') as f:
                connection.executescript(f.read())
            connection.commit()
            connection.close()
            print("Database initialized automatically from schema.sql!")


def create_app():

    # =========================================================
    # LOAD ENVIRONMENT VARIABLES
    # =========================================================

    load_dotenv()

    # =========================================================
    # AUTO-INITIALIZE DATABASE ON STARTUP (RENDER FIX)
    # =========================================================
    init_db_on_startup()

    # =========================================================
    # CREATE FLASK APP
    # =========================================================

    app = Flask(__name__)

    # =========================================================
    # FLASK CONFIGURATION
    # =========================================================

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

    # =========================================================
    # RETURN APP
    # =========================================================

    return app