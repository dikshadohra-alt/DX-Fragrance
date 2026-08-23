import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# Yeh class psycopg2 connection ko SQLite jaisa banati hai taaki .execute() direct chal sake
class PostgreSQLCursorWrapper:

    def __init__(self, conn):
        self.conn = conn
        self.cursor_obj = conn.cursor()

    def execute(self, query, params=None):
        # SQLite ke '?' ko PostgreSQL ke '%s' mein badalne ke liye agar zaroorat ho,
        # ya direct execute karne ke liye:
        # Note: psycopg2 ? placeholder ko bhi support karta hai agar adaptors hain,
        # par agar error aaye toh niche wala standard use karein:
        formatted_query = query.replace("?", "%s")
        if params:
            self.cursor_obj.execute(formatted_query, params)
        else:
            self.cursor_obj.execute(formatted_query)
        return self

    def fetchall(self):
        return self.cursor_obj.fetchall()

    def fetchone(self):
        return self.cursor_obj.fetchone()

    def commit(self):
        return self.conn.commit()

    def close(self):
        self.cursor_obj.close()
        self.conn.close()


class PostgreSQLConnectionWrapper:

    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=None):
        wrapper = PostgreSQLCursorWrapper(self.conn)
        return wrapper.execute(query, params)

    def commit(self):
        return self.conn.commit()

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        return self.conn.close()


def get_db_connection():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(
            DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor
        )
        return PostgreSQLConnectionWrapper(conn)
    else:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn