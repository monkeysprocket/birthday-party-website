from typing import Any

from botocore.exceptions import ClientError
from werkzeug.security import generate_password_hash

from lambda_functions.admin.app.check_auth import check_auth

USERNAME = "admin"
PASSWORD = "supersecret"

class MockTable:
    def __init__(self, raises=False) -> None:
        self._raises = raises

    def get_item(self, Key: dict[str, Any]) -> dict[str, Any]:
        if self._raises:
            raise ClientError({"Error": {"Message": "ThisIsATestError"}}, "")
        if Key["username"] == USERNAME:
            return {"Item" :{"username": USERNAME, "password_hash": generate_password_hash(PASSWORD)}}
        else:
            return {}


class TestCheckAuth:
    def test_valid_credentials_returns_true(self):
        result = check_auth(username=USERNAME, password=PASSWORD, table=MockTable())

        assert result is True

    def test_invalid_username_returns_false(self):
        result = check_auth(username="invalid", password=PASSWORD, table=MockTable())

        assert result is False

    def test_invalid_password_returns_false(self):
        result = check_auth(username=USERNAME, password="invalid", table=MockTable())

        assert result is False
