from app import create_app
from config.database import get_db_connection

app = create_app()

# Wishlist table safety check
with app.app_context():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """
    )
    connection.commit()
    connection.close()


if __name__ == "__main__":
    app.run(debug=True)