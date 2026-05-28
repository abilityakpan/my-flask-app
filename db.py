import os
import sqlite3
from flask import g

def get_db():
    if 'db' not in g:
        # Opens a local database file named 'database.db' in your project root
        g.db = sqlite3.connect('database.db')
        # This allows us to fetch data as handy dictionaries (like row['email'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    # Safely close the database connection if it exists
    db = g.pop('db', None)
    if db is not None:
        db.close()
