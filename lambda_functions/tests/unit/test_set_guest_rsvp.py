import uuid
from typing import Any

from botocore.exceptions import ClientError

from lambda_functions.update_guest_rsvp.update_guest_rsvp import set_guest_rsvp

GUEST_UUID = uuid.uuid4().hex
GUEST_NAME = "alice"


class MockTable:
    def __init__(self, guest_uuid: str | None, raises=False) -> None:
        self._guest_uuid = guest_uuid
        self._raises = raises
        self.update_successful = False

    def update_item(
            self,
            Key: dict[str, Any],
            UpdateExpression: str,
            ExpressionAttributeValues: dict[str, str],
            ConditionExpression: str,
    ) -> dict[str, Any]:
        if self._raises:
            raise ClientError({"Error": {"Message": "ThisIsATestError"}}, "")
        if Key["id"] == self._guest_uuid:
            self.update_successful = True
        else:
            return {}


class TestUpdateGuestRSVP:
    """
    Absolutely no point in this as I've mocked out the only functionality in the function. covered by integration tests.
    """
    def test_guest_exists(self):
        table = MockTable(guest_uuid=GUEST_UUID)

        set_guest_rsvp(GUEST_UUID, "yes", "message", table)

        assert table.update_successful is True
