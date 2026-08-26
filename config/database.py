import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


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



def get_db_connection():

    # ========================================================
    # POSTGRESQL
    # ========================================================

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

    # ========================================================
    # SQLITE - LOCAL DEVELOPMENT
    # ========================================================

    conn = sqlite3.connect(
        "database/dx_fragrance.db"
    )

    conn.row_factory = sqlite3.Row

    return conn