import os
import sqlite3

def get_db_connection():
    # Project ke main directory ka absolute path calculate karna
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'database', 'dx_fragrance.db')
    
    # Connection banao
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection