import sqlite3
import uuid

def setup():
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


def foo():
    conn = sqlite3.connect("guests.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * from guests")
    for row in cursor.fetchall():
        print(row)


if __name__ == "__main__":
    foo()
    