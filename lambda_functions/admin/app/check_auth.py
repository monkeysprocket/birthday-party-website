from typing import Any, Protocol

from werkzeug.security import check_password_hash


class TableLike(Protocol):
    def get_item(self, Key: dict[str, Any]) -> dict[str, Any]: ...


def check_auth(username: str, password: str, table: TableLike) -> bool:
    response = table.get_item(Key={"username": username})
    item = response.get("Item")

    if not item:
        return False
    else:
        return check_password_hash(item["password_hash"], password)
