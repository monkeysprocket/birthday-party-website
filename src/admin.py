from functools import wraps
from flask import request, Response
import sqlite3
from werkzeug.security import check_password_hash


def check_auth(username: str, password: str) -> bool:
    conn = sqlite3.connect('guests.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False
    
    password_hash = row[0]
    return check_password_hash(password_hash, password)


def authenticate():
    return Response(
        "Access denied", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
