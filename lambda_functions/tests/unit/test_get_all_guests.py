from typing import Any

from botocore.exceptions import ClientError

from lambda_functions.admin.app.get_all_guests import get_all_guests

USERNAME = "admin"
PASSWORD = "supersecret"

class MockTable:
    USERS = [
        {
            "name": "Amy",
            "email": "amy@example.com",
            "rsvp_status": "yes",
            "rsvp_message": "can't wait!",
        },
        {
            "name": "Barry",
            "email": "barry@example.com",
            "rsvp_status": "no",
        },
    ]

    def __init__(self, users: list[dict[str, str]], raises=False) -> None:
        self.users = users
        self._raises = raises

    def scan(self, ProjectionExpression: str, ExpressionAttributeNames: dict[str, str]) -> dict[str, list[dict[str, Any]]]:
        if self._raises:
            raise ClientError({"Error": {"Message": "ThisIsATestError"}}, "")
        else:
            return {"Items": self.users}


class TestCheckAuth:
    def test_single_user(self):
        user = {
            "name": "Amy",
            "email": "amy@example.com",
            "rsvp_status": "yes",
            "rsvp_message": "can't wait!",
        }
        table = MockTable(users=[user])

        results = get_all_guests(table)

        assert len(results) == 1

        result = results[0]

        assert result[0] == user["name"]
        assert result[1] == user["email"]
        assert result[2] == user["rsvp_status"]
        assert result[3] == user["rsvp_message"]

    def test_multiple_users(self):
        users = [
            {
                "name": "Amy",
                "email": "amy@example.com",
                "rsvp_status": "yes",
                "rsvp_message": "can't wait!",
            },
            {
                "name": "Barry",
                "email": "barry@example.com",
                "rsvp_status": "no",
            },
        ]
        table = MockTable(users=users)

        results = get_all_guests(table)

        assert len(results) == len(users)

        for index, result in enumerate(results):
            expected = users[index]

            assert result[0] == expected["name"]
            assert result[1] == expected["email"]
            assert result[2] == expected["rsvp_status"]
            assert result[3] == expected.get("rsvp_message", "")

    def test_no_rsvp_message_returns_empty_str(self):
        user = {
            "name": "Amy",
            "email": "amy@example.com",
            "rsvp_status": "yes",
        }
        table = MockTable(users=[user])

        results = get_all_guests(table)

        assert len(results) == 1

        result = results[0]

        assert result[3] == ""

    def test_no_users(self):
        table = MockTable(users=[])

        results = get_all_guests(table)

        assert len(results) == 0
