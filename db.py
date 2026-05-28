"""
SQLite Database Module for Tesla Giveaway Flask Application
Optimized for Render deployment with persistent disk
"""

import os
import sqlite3
from flask import current_app

# Use Render's persistent disk path if available, otherwise use local path
if os.getenv("RENDER"):
    # On Render, use the persistent disk mount point
    DATABASE = os.path.join(os.getenv("RENDER_DISK_MOUNT_POINT", "/mnt/disk"), "database.db")
else:
    # Local development
    DATABASE = 'database.db'


def get_db():
    """Get database connection with SQLite Row factory for dict-like access."""
    if 'db' not in current_app.g:
        # Ensure directory exists
        os.makedirs(os.path.dirname(DATABASE) if os.path.dirname(DATABASE) else '.', exist_ok=True)
        current_app.g.db = sqlite3.connect(DATABASE)
        current_app.g.db.row_factory = sqlite3.Row
    return current_app.g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = current_app.g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """
    Initialize database with all required tables for the Tesla giveaway app.
    Call this once when Flask app starts.
    """
    # Ensure directory exists
    db_dir = os.path.dirname(DATABASE)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # TABLE 1: claims - User participation data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL,
                zip_postal TEXT NOT NULL,
                promo_code TEXT,
                address TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # TABLE 2: admins - Admin authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # TABLE 3: testimonials - Customer testimonials
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS testimonials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                time_text TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # TABLE 4: payments - Payment records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id INTEGER,
                amount TEXT NOT NULL,
                method TEXT NOT NULL,
                payment_status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (claim_id) REFERENCES claims(id)
            )
        """)
        
        # TABLE 5: site_settings - Configurable settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
        """)
        
        # Insert default admin (email: admin@tesla.com, password: admin)
        cursor.execute("""
            INSERT OR IGNORE INTO admins (id, email, password_hash, full_name, created_at)
            VALUES (1, 'admin@tesla.com', 'scrypt:32768:8:1$qJFadhyH8KgMajwt$05e24e36e6b70f9958156193796da034639b56fceb5c472cbf0823351996f0ab5a38ecbe6e8973db129e0004ccb708608e6be018788c03e54b68ff52843b0923', 'Tesla Admin', '2026-05-21 17:58:30')
        """)
        
        # Insert default settings
        default_settings = [
            ('site_name', 'Tesla Motors'),
            ('whatsapp_number', '2348012345678'),
            ('hero_joined_count', '12,907'),
            ('event_live_count', '12,919'),
            ('delivery_fee_note', 'Covers shipping, customs & logistics'),
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO site_settings (setting_key, setting_value)
            VALUES (?, ?)
        """, default_settings)
        
        conn.commit()
        print(f"Database initialized successfully at: {DATABASE}")


if __name__ == "__main__":
    init_db()
