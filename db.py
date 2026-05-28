try:
    import mysql.connector
except ImportError as exc:
    raise RuntimeError(
        "Missing required dependency 'mysql-connector-python'. "
        "Install it with `pip install mysql-connector-python`."
    ) from exc

from flask import g, current_app

def get_db():
    if "db" not in g or not g.db.is_connected():
        g.db = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE"],
        )
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()v