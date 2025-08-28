from typing import Any, Protocol


class TableLike(Protocol):
    def scan(self, ProjectionExpression: str, ExpressionAttributeNames: dict[str, str]) -> dict[str, list[dict[str, Any]]]: ...


def get_all_guests(table: TableLike) -> list[tuple[str, str, str, str]]:
    response = table.scan(
        ProjectionExpression="#n, email, rsvp_status, rsvp_message",
        ExpressionAttributeNames={"#n": "name"},
    )
    return [
        (item["name"], item["email"], item.get("rsvp_status", "pending"), item.get("rsvp_message", ""))
        for item in response.get("Items", [])
    ]