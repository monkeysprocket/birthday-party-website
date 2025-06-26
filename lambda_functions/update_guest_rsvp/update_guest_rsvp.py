import json
import os
import urllib.parse
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


class ParsingError(Exception):
    def __init__(self, raw_body: str) -> None:
        self.raw_body = raw_body

    def __str__(self) -> str:
        return f"Failed to parse application/x-www-form-urlencoded data: '{self.raw_body}'"


dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

def lambda_handler(event: Event, _) -> dict[str, int | str]:
    try:
        uuid, rsvp, message = parse_form_body(raw_body=event.get("body"))
    except ParsingError as e:
        return generate_response(
            body={"error": str(e)}, status_code=400
        )

    try:
        set_guest_rsvp(uuid, rsvp, message, dynamodb_table)
    except ClientError as e:
        if "ConditionalCheckFailedException" in str(e):
            return generate_response(body={"error": "UpdateItem failed: guest uuid not found"}, status_code=400)
        else:
            return generate_response(body={"error": e.response['Error']['Message']}, status_code=500)
    else:
        return redirect(to=f"/invite/{uuid}?rsvp_thanks=true")


def parse_form_body(raw_body: str) -> tuple[str, str, str | None]:
    try:
        form = urllib.parse.parse_qs(raw_body, keep_blank_values=True, strict_parsing=True)
        uuid = form["uuid"][0]
        rsvp = form["rsvp"][0]
        message = form["message"][0] or None
    except (ValueError, KeyError):
        raise ParsingError(raw_body=raw_body)
    else:
        return uuid, rsvp, message


def set_guest_rsvp(uuid: str, rsvp: str, message: str, table: TableLike) -> None:
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


def redirect(to: str) -> dict[str, str | int]:
    return {
        "statusCode": 301,
        "headers": {
            "Location": to,
        }
    }
