import json
import os
from typing import TypedDict, Optional, Protocol, Any

import boto3
from botocore.exceptions import ClientError


class Event(TypedDict):
    uuid: Optional[str]


class TableLike(Protocol):
    def get_item(self, Key: dict[str, Any]) -> dict[str, Any]: ...


dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])


def lambda_handler(event: Event, _) -> dict[str, int | str]:
    uuid = event.get("uuid")
    if not uuid:
        return generate_response(body={"error": "Missing 'uuid' in request"}, status_code=400)

    try:
        guest_name = get_guest_name_from_invite_uuid(uuid, dynamodb_table)
    except ClientError as e:
        return generate_response(body={"error": e.response['Error']['Message']}, status_code=500)
    else:
        if guest_name:
            return generate_response(body={"name": guest_name}, status_code=200)
        else:
            return generate_response(body={"error": "Guest not found"}, status_code=404)


def get_guest_name_from_invite_uuid(uuid: str, table: TableLike) -> str | None:
    response = table.get_item(Key={"id": uuid})
    item = response.get("Item")

    if not item:
        return None
    else:
        return item["name"]


def generate_response(body: dict[str, str], status_code: int):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
    }