import sqlite3
import uuid
from werkzeug.security import generate_password_hash

def setup_guests_table():
    guests = [
        ("Alice" ,"alice@example.com"),
        ("Bob", "bob@example.com"),
    ]

    conn = sqlite3.connect("guests.db")
    cursor = conn.cursor()

    cursor.execute("""\
    CREATE TABLE IF NOT EXISTS guests (
        uuid TEXT PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        rsvp_Status TEXT DEFAULT 'pending',
        rsvp_message TEXT
        )
    """)

    for name, email in guests:
        guest_uuid = str(uuid.uuid4())
        cursor.execute("INSERT INTO guests (uuid, name, email) VALUES (?, ?, ?)", (guest_uuid, name, email))
        print(f"{name}: http://127.0.0.1:5000//invite/{guest_uuid}")

    conn.commit()
    conn.close()


def setup_users_table(admin_password: str) -> None:
    conn = sqlite3.connect("guests.db")
    cursor = conn.cursor()

    cursor.execute("""\
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
        )
    """)

    username = "admin"
    password_hash = generate_password_hash(admin_password)

    cursor.execute("INSERT OR REPLACE INTO users (id, username, password_hash) VALUES (1, ?, ?)", (username, password_hash))
    conn.commit()
    conn.close()


def foo():
    conn = sqlite3.connect("guests.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * from guests")
    for row in cursor.fetchall():
        print(row)


if __name__ == "__main__":
    foo()
    