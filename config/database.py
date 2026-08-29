import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# =========================================================
# POSTGRESQL CURSOR WRAPPER
# =========================================================

class PostgreSQLCursorWrapper:

    def __init__(self, conn):
        self.conn = conn
        self.cursor_obj = conn.cursor()
        self._lastrowid = None

    def execute(self, query, params=None):

        formatted_query = query.replace("?", "%s")

        is_insert = (
            formatted_query.strip()
            .upper()
            .startswith("INSERT")
        )

        # PostgreSQL needs RETURNING id for lastrowid
        if (
            is_insert
            and "RETURNING" not in formatted_query.upper()
        ):
            formatted_query = (
                formatted_query.rstrip(";")
                + " RETURNING id"
            )

        if params is not None:
            self.cursor_obj.execute(
                formatted_query,
                params
            )
        else:
            self.cursor_obj.execute(
                formatted_query
            )

        # Get generated ID only for INSERT
        if is_insert:

            try:
                row = self.cursor_obj.fetchone()

                if row:
                    self._lastrowid = row[0]

            except Exception:
                self._lastrowid = None

        return self

    # =====================================================
    # LAST INSERT ID
    # =====================================================

    @property
    def lastrowid(self):
        return self._lastrowid

    # =====================================================
    # ROW COUNT
    # =====================================================

    @property
    def rowcount(self):
        return self.cursor_obj.rowcount

    # =====================================================
    # FETCH
    # =====================================================

    def fetchall(self):
        return self.cursor_obj.fetchall()

    def fetchone(self):
        return self.cursor_obj.fetchone()

    # =====================================================
    # COMMIT / CLOSE
    # =====================================================

    def commit(self):
        return self.conn.commit()

    def close(self):
        return self.cursor_obj.close()


# =========================================================
# POSTGRESQL CONNECTION WRAPPER
# =========================================================

class PostgreSQLConnectionWrapper:

    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=None):

        wrapper = PostgreSQLCursorWrapper(
            self.conn
        )

        return wrapper.execute(
            query,
            params
        )

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        return self.conn.close()


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    # =====================================================
    # POSTGRESQL - RENDER / PRODUCTION
    # =====================================================

    if DATABASE_URL:

        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=psycopg2.extras.DictCursor
        )

        return PostgreSQLConnectionWrapper(
            conn
        )

    # =====================================================
    # SQLITE - LOCAL DEVELOPMENT
    # =====================================================

    conn = sqlite3.connect(
        "database/dx_fragrance.db"
    )

    conn.row_factory = sqlite3.Row

    return conn