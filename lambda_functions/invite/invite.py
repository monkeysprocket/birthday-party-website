import json
import os
from typing import TypedDict, Protocol, Any
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from jinja2 import Environment, FileSystemLoader, select_autoescape


class PathParameters(TypedDict):
    uuid: str | None


class QueryStringParameters(TypedDict):
    rsvp_thanks: bool


class Event(TypedDict):
    pathParameters: PathParameters | None
    queryStringParameters: QueryStringParameters | None


class TableLike(Protocol):
    def get_item(self, Key: dict[str, Any]) -> dict[str, Any]: ...


dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ["DYNAMODB_GUESTS_TABLE"])

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(),
)
template = env.get_template("invite.html")


def lambda_handler(event: Event, _) -> dict[str, int | str]:
    uuid = event.get("pathParameters", {}).get("uuid")
    if not uuid:
        return generate_json_response(body={"error": "Missing 'uuid' in request"}, status_code=400)

    try:
        guest_name = get_guest_name_from_invite_uuid(uuid, users_table)
    except ClientError as e:
        return generate_json_response(body={"error": e.response['Error']['Message']}, status_code=500)

    if guest_name is None:
        return generate_json_response(body={"error": "Guest not found"}, status_code=404)

    rsvp_thanks = (event.get("queryStringParameters") or {}).get("rsvp_thanks", False)

    return generate_html_response(
        body=template.render(guest_name=guest_name, uuid=uuid, rsvp_thanks=rsvp_thanks),
        status_code=200,
    )


def generate_html_response(body: str, status_code: int):
    return {
        "statusCode": status_code,
        "body": body,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
        },
    }

def generate_json_response(body, status_code: int):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://party.matthewjamesquinn.com",
        },

    }

def get_guest_name_from_invite_uuid(uuid: str, table: TableLike) -> str | None:
    response = table.get_item(Key={"id": uuid})
    item = response.get("Item")

    if not item:
        return None
    else:
        return item["name"]