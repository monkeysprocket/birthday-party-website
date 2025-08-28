import base64
from binascii import Error as BinasciiError


class AuthHeaderParsingError(Exception):
    pass


def get_username_and_password_from_basic_auth_header(auth_header: str) -> tuple[str, str]:
    try:
        encoded_credentials = auth_header.split(" ")[1]
        decoded = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded.split(":", 1)
    except (IndexError, BinasciiError, ValueError):
        raise AuthHeaderParsingError(f"Unexpected auth header format: '{auth_header}'")
    return username, password
