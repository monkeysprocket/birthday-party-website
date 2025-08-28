import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(),
)
template = env.get_template("index.html")


def lambda_handler(*_) -> dict[str, int | str]:
    return generate_response(body=template.render(), status_code=200)


def generate_response(body: str, status_code: int):
    return {
        "statusCode": status_code,
        "body": body,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN"),
        },

    }