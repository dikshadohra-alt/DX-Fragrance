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
        self._lastrowid = None

    def execute(self, query, params=None):
        formatted_query = query.replace("?", "%s")
        
        # Agar INSERT query hai aur RETURNING id nahi hai, toh PostgreSQL ke liye add kar dete hain taaki lastrowid mil jaye
        if "INSERT" in formatted_query.upper() and "RETURNING" not in formatted_query.upper():
            formatted_query = formatted_query.rstrip(";") + " RETURNING id"
            
        if params:
            self.cursor_obj.execute(formatted_query, params)
        else:
            self.cursor_obj.execute(formatted_query)
            
        # Agar INSERT tha toh ID fetch kar lete hain
        try:
            row = self.cursor_obj.fetchone()
            if row and "id" in row:
                self._lastrowid = row["id"]
            elif row and len(row) > 0:
                self._lastrowid = row[0]
        except Exception:
            pass
            
        return self

    @property
    def lastrowid(self):
        return self._lastrowid

    def fetchall(self):
        try:
            return self.cursor_obj.fetchall()
        except Exception:
            return []

    def fetchone(self):
        try:
            return self.cursor_obj.fetchone()
        except Exception:
            return None

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