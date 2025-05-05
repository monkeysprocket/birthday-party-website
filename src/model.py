import sqlite3
from uuid import UUID
from werkzeug.security import generate_password_hash

from exceptions import NotFoundError


class Model:
    def __init__(self, connection_string: str, admin_password: str) -> None:
        self._connection_string = connection_string

        self._setup_db(admin_password)
    
    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._connection_string)
    
    def get_guest_by_uuid(self, uuid: UUID) -> str:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM guests WHERE uuid = ?", (uuid,))
            row = cursor.fetchone()
            if not row:
                raise NotFoundError
            else:
                return row[0]
    
    def get_all_guests(self):
         with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, email, rsvp_status, rsvp_message FROM guests ORDER BY name")
            guests = cursor.fetchall()
            return guests
    
    def update_guest_rsvp(self, uuid: UUID, rsvp: str, message: str) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""\
            UPDATE guests 
            SET 
                rsvp_status = ?,
                rsvp_message = ?
            WHERE uuid = ?
            """,
            (rsvp, message, uuid),
            )
            conn.commit()

    def _setup_db(self, admin_password: str) -> None:
        print("setting up db")
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""\
            CREATE TABLE IF NOT EXISTS guests (
                uuid TEXT PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE,
                rsvp_status TEXT DEFAULT 'pending',
                rsvp_message TEXT
            )"""
                )

            cursor.execute("""\
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )"""
                )
            
            username = "admin"
            if not admin_password:
                raise RuntimeError("ADMIN_PASSWORD environment variable is not set")
            password_hash = generate_password_hash(admin_password)

            cursor.execute("INSERT OR REPLACE INTO users (id, username, password_hash) VALUES (1, ?, ?)", (username, password_hash))
            conn.commit()
