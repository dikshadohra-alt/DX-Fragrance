import sqlite3

from config.settings import Config


def get_db_connection():
    connection = sqlite3.connect(Config.DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection