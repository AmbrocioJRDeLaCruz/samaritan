import os
import sqlite3
from functools import wraps
from flask import redirect, session

DB_NAME = "samaritan.db"


def get_db():
    """
    Retorna una conexión a la base de datos SQLite.
    Configura sqlite3.Row para acceder a las columnas por nombre (como diccionarios).
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Inicializa la base de datos ejecutando schema.sql si las tablas no existen.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db() as conn:
        conn.executescript(schema_sql)


def login_required(f):
    """
    Decorador estándar de CS50 para proteger rutas que requieren autenticación.
    Si el usuario no ha iniciado sesión en session["user_id"], redirige a /login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
