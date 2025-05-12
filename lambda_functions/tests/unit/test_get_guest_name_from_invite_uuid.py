import uuid
from typing import Any

from botocore.exceptions import ClientError

from lambda_functions.get_guest_name_from_invite_uuid.app import get_guest_name_from_invite_uuid, lambda_handler

GUEST_UUID = uuid.uuid4().hex
GUEST_NAME = "alice"


class MockTable:
    def __init__(self, guest_exists=True, raises=False) -> None:
        self._guest_exists = guest_exists
        self._raises = raises

    def get_item(self, Key: dict[str, Any]) -> dict[str, Any]:
        if self._raises:
            raise ClientError({"Error": {"Message": "ThisIsATestError"}}, "")
        if self._guest_exists:
            return {"Item" :{"name": "alice"}}
        else:
            return {}


class TestLambdaGetGuestByUUID:
    def test_guest_exists(self):
        table = MockTable()

        result = get_guest_name_from_invite_uuid(GUEST_UUID, table)

        assert result == GUEST_NAME

    def test_guest_does_not_exist(self):
        table = MockTable(guest_exists=False)

        result = get_guest_name_from_invite_uuid(GUEST_UUID, table)

        assert result is None
