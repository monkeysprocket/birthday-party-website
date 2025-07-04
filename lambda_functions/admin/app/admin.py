import json
import os
from pathlib import Path
from typing import TypedDict, Any

import boto3
from botocore.exceptions import ClientError
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .auth_header_parsing import get_username_and_password_from_basic_auth_header, AuthHeaderParsingError
from .check_auth import check_auth
from .get_all_guests import get_all_guests

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ["DYNAMODB_USERS_TABLE"])
guests_table = dynamodb.Table(os.environ["DYNAMODB_GUESTS_TABLE"])

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / "templates"),
    autoescape=select_autoescape(),
)
template = env.get_template("admin.html")


class EventHeaders(TypedDict):
    authorization: str


class Event(TypedDict):
    headers: EventHeaders


def lambda_handler(event: Event, _) -> dict[str, Any]:
    auth_header: str = event.get("headers", {}).get("authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return generate_unauthorized_response()

    try:
        username, password = get_username_and_password_from_basic_auth_header(auth_header=auth_header)
    except AuthHeaderParsingError as e:
        return generate_json_response(body={"error": f"Error reading auth header: {e}"}, status_code=500)
    except Exception as e:
        return generate_json_response(body={"error": f"Unhandled Exception: {e}"}, status_code=500)

    try:
        if not check_auth(username=username, password=password, table=users_table):
            return generate_unauthorized_response()
    except ClientError as e:
        return generate_json_response(body={"error": f"Error while accessing users table: {e.response['Error']['Message']}"}, status_code=500)

    try:
        guests = get_all_guests(guests_table)
    except ClientError as e:
        return generate_json_response(body={"error": f"Error while accessing guests table: {e.response['Error']['Message']}"}, status_code=500)

    return generate_html_response(
        body=template.render(guests=guests),
        status_code=200,
    )


def generate_unauthorized_response():
    return {
        "statusCode": 401,
        "body": "Access Denied",
        "headers": {
            "WWW-Authenticate": 'Basic realm="Admin"',
            "Content-Type": "text/plain",
            "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
            "Access-Control-Expose-Headers": "WWW-Authenticate",
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


def generate_html_response(body: str, status_code: int):
    return {
        "statusCode": status_code,
        "body": body,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
        },
    }
