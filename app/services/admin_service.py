from config.database import get_db_connection
from werkzeug.security import generate_password_hash


class AdminService:

    @staticmethod
    def get_admin(admin_id):

        connection = get_db_connection()

        admin = connection.execute(
            """
            SELECT
                id,
                username AS name,
                email,
                NULL AS phone,
                NULL AS created_at
            FROM users
            WHERE id = ?
              AND is_admin = 1
            """,
            (admin_id,)
        ).fetchone()

        connection.close()

        return admin


    @staticmethod
    def change_password(admin_id, new_password):

        connection = get_db_connection()

        password_hash = generate_password_hash(new_password)

        connection.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
              AND is_admin = 1
            """,
            (password_hash, admin_id)
        )

        connection.commit()
        connection.close()

        return True