import json
import os
from typing import TypedDict, Protocol, Any

import boto3
from botocore.exceptions import ClientError


class Event(TypedDict):
    body: str | None


class TableLike(Protocol):
    def update_item(
            self,
            Key: dict[str, Any],
            UpdateExpression: str,
            ExpressionAttributeValues: dict[str, str],
            ConditionExpression: str,
    ) -> dict[str, Any]: ...


dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

def lambda_handler(event: Event, _) -> dict[str, int | str]:
    try:
        body = json.loads(event.get("body"))
    except json.JSONDecodeError:
        return generate_response({"error": "Invalid JSON in request body"}, status_code=400)

    uuid = body.get("uuid")
    rsvp = body.get("rsvp")
    message = body.get("message")

    if not uuid:
        return generate_response(body={"error": "Missing 'uuid' in request"}, status_code=400)
    if not rsvp:
        return generate_response(body={"error": "Missing 'rsvp' in request"}, status_code=400)

    try:
        update_guest_rsvp(uuid, rsvp, message, dynamodb_table)
    except ClientError as e:
        if "ConditionalCheckFailedException" in str(e):
            return generate_response(body={"error": "UpdateItem failed: guest uuid not found"}, status_code=500)
        else:
            return generate_response(body={"error": e.response['Error']['Message']}, status_code=500)
    else:
        return generate_response(body={"message": "OK"}, status_code=200)


def update_guest_rsvp(uuid: str, rsvp: str, message: str, table: TableLike) -> None:
    table.update_item(
        Key={"id": str(uuid)},
        UpdateExpression="SET rsvp_status = :r, rsvp_message = :m",
        ExpressionAttributeValues={
            ":r": rsvp,
            ":m": message
        },
        ConditionExpression="attribute_exists(id)",
    )


def generate_response(body: dict[str, str], status_code: int):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
        },

    }