import json
import logging
import os
from typing import TypedDict, Any

import boto3
from botocore.exceptions import ClientError

from .auth_header_parsing import get_username_and_password_from_basic_auth_header, AuthHeaderParsingError
from .check_auth import check_auth
from .form_body_parsing import parse_form_body, get_body, FormBodyParsingError
from .add_guest import add_guest
from.send_email import send_invite_email

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ["DYNAMODB_USERS_TABLE"])
guests_table = dynamodb.Table(os.environ["DYNAMODB_GUESTS_TABLE"])

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class EventHeaders(TypedDict):
    authorization: str


class Event(TypedDict):
    headers: EventHeaders
    isBase64Encoded: bool
    body: str


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
        name, email = parse_form_body(raw_body=get_body(event))
    except FormBodyParsingError as e:
        return generate_json_response(body={"error": str(e)}, status_code=400)

    try:
        new_guest_uuid = add_guest(name=name, email=email, table=guests_table)
    except ValueError as e:
        generate_json_response(body={"error": str(e)}, status_code=400)
    except ClientError as e:
        return generate_json_response(
            body={"error": f"Error while accessing users table: {e.response['Error']['Message']}"}, status_code=500)

    try:
        send_invite_email(name, email, new_guest_uuid)
    except Exception as e:
        return redirect_to_admin(error=f"Failed to send invite to {email}. {e}")

    return redirect_to_admin(success=f"Invite sent to {email}.")



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


def redirect_to_admin(success:str = None, error: str = None) -> dict[str, str | int]:
    foo = {
        "statusCode": 301,
        "headers": {
            "Location": "/admin",
        },
        "body": json.dumps({"success": success, "error": error})
    }
    logger.info(str(foo))
    return foo
