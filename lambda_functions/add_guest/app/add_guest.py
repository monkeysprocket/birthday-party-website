from typing import Protocol, Any
from uuid import uuid4

from botocore.exceptions import ClientError


class TableLike(Protocol):
    def put_item(self, Item: dict[str, Any], ConditionExpression: str) -> dict[str, Any]: ...


def add_guest(name: str, email: str, table: TableLike) -> str:
    new_guest_uuid = uuid4().hex
    item = {
        "id": new_guest_uuid,
        "name": name,
        "email": email,
        "rsvp_status": "pending",
    }

    try:
        table.put_item(Item=item, ConditionExpression="attribute_not_exists(email)")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise ValueError("Guest with this email already exists.")
        else:
            raise
    return new_guest_uuid
