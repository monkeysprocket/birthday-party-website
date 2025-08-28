import base64
import urllib.parse
from typing import TypedDict


class Event(TypedDict):
    isBase64Encoded: bool
    body: str


class FormBodyParsingError(Exception):
    def __init__(self, raw_body: str) -> None:
        self.raw_body = raw_body

    def __str__(self) -> str:
        return f"Failed to parse application/x-www-form-urlencoded data: '{self.raw_body}'"



def get_body(event: Event) -> str:
    if event.get("isBase64Encoded"):
        return base64.b64decode(event.get("body")).decode("utf-8")
    else:
        return event.get("body")


def parse_form_body(raw_body: str) -> tuple[str, str]:
    try:
        form = urllib.parse.parse_qs(raw_body, keep_blank_values=True, strict_parsing=True)
        name = form["name"][0]
        email = form["email"][0]
    except (ValueError, KeyError):
        raise FormBodyParsingError(raw_body=raw_body)
    else:
        return name, email
