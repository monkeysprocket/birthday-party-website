import os
import sqlite3
import uuid

import pytest

from src.exceptions import IncompleteDataError
from src.model import Model


@pytest.fixture()
def model() -> Model:
    test_db_path = "test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = Model(connection_string=test_db_path, admin_password="password")

    yield db
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


class TestGetAllGuests:
    GUEST_1_UUID = uuid.uuid4().hex
    GUEST_1_NAME = "bob"
    GUEST_2_UUID = uuid.uuid4().hex
    GUEST_2_NAME = "charlie"

    def test_guest_list_empty(self, model):
        result = model.get_all_guests()

        assert result == []
    
    def test_with_guests(self, model):
        with model._connect() as conn:
            _add_guest(conn, self.GUEST_1_UUID, self.GUEST_1_NAME)
            _add_guest(conn, self.GUEST_2_UUID, self.GUEST_2_NAME)

        result = model.get_all_guests()

        assert isinstance(result, list)
        assert len(result) == 2


class TestAddGuest:
    GUEST_NAME = "david"
    GUEST_EMAIL = "david@example.com"

    def test_happy_path(self, model):
        new_guest_uuid = model.add_guest(name=self.GUEST_NAME, email=self.GUEST_EMAIL)

        with model._connect() as conn:
            guest = _get_guest_by_uuid(conn, new_guest_uuid)

        assert guest is not None
        assert guest["name"] == self.GUEST_NAME
        assert guest["email"] == self.GUEST_EMAIL 
    
    def test_no_name_raises(self, model):
        with pytest.raises(IncompleteDataError):
            model.add_guest(name=None, email=self.GUEST_EMAIL)
    
    def test_no_email_raises(self, model):
        with pytest.raises(IncompleteDataError):
            model.add_guest(name=self.GUEST_NAME, email=None)


def _add_guest(conn: sqlite3.Connection, uuid: str, name: str) -> None:
        cur = conn.cursor()
        cur.execute("INSERT INTO guests (uuid, name) VALUES (?, ?)", (uuid, name))
        conn.commit()

def _get_guest_by_uuid(conn: sqlite3.Connection, uuid: str) -> dict[str]:
    cur = conn.cursor()
    cur.execute("SELECT name, email, rsvp_status, rsvp_message FROM guests WHERE uuid = ?", (uuid,))
    result = cur.fetchone()
    return {
        "name": result[0],
        "email": result[1],
        "rsvp_status": result[2],
        "rsvp_message": result[3],
    }
