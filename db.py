import os
import sqlite3
from flask import g

def get_db():
    if 'db' not in g:
        # This looks for a local database file named 'database.db'
        g.db = sqlite3.connect('database.db')
        # This tells SQLite to return rows as dictionaries (so you can access them like row['email'])
        g.db.row_factory = sqlite3.Row
    return g.db
