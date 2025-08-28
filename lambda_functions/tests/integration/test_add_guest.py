import base64
import json
from unittest.mock import patch
from uuid import uuid4

import pytest
from botocore.exceptions import ClientError

from lambda_functions.add_guest.app.main import lambda_handler, users_table
from lambda_functions.add_guest.app.send_email import ses

TEST_GUEST = "test"

@pytest.fixture()
def client_error():
    with patch.object(users_table, "update_item") as mock_get_item:
        mock_get_item.side_effect = ClientError(
            error_response={"Error": {"Message": "Simulated failure"}},
            operation_name="GetItem"
        )
        yield

@pytest.fixture(scope="module", autouse=True)
def email_mock():
    # mocks ses.send_email to prevent actual emails being sent during tests
    with patch.object(ses, "send_email"):
        yield


def clean_up_test_guest(table, name: str) -> None:
    test_guest_id = get_test_guest_id(table)

    if test_guest_id is None:
        print("no test user to clean up")
    else:
        table.delete_item(Key={"id": test_guest_id})
        print("cleaned up test user")


def get_test_guest_id(table) -> str | None:
    response = table.scan(
        ProjectionExpression="id",
        FilterExpression=f"#n = :name",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={":name": TEST_GUEST}
    )
    print(response)

    if response.get("Count", 0) == 0:
        print("no test guest to clean up")
        return None
    else:
        print("test guest id found")
        return response["Items"][0]["id"]


class TestLambdaHandler:
    def test_guest_added_to_database(self, user, guests_table):
        event = {
            "headers": {
                "authorization": "Basic " + base64.b64encode(f"{user["username"]}:{user["password"]}".encode()).decode()
            },
            "body": base64.b64encode(f"name={TEST_GUEST}&email={TEST_GUEST}@example.com".encode()).decode(),
            "isBase64Encoded": True,
        }

        lambda_handler(event, None)

        test_guest_id = get_test_guest_id(guests_table)

        test_user = guests_table.get_item(Key={"id": test_guest_id}).get("Item")

        clean_up_test_guest(guests_table, "test")

        assert test_user["name"] == TEST_GUEST
        assert test_user["email"] == f"{TEST_GUEST}@example.com"

    def test_success_redirects(self, user, guests_table):
        event = {
            "headers": {
                "authorization": "Basic " + base64.b64encode(f"{user["username"]}:{user["password"]}".encode()).decode()
            },
            "body": base64.b64encode(f"name={TEST_GUEST}&email={TEST_GUEST}@example.com".encode()).decode(),
            "isBase64Encoded": True,
        }

        result = lambda_handler(event, None)

        clean_up_test_guest(guests_table, "test")

        assert result["statusCode"] == 301

    def test_success_redirect_has_message_in_body(self, user, guests_table):
        event = {
            "headers": {
                "authorization": "Basic " + base64.b64encode(f"{user["username"]}:{user["password"]}".encode()).decode()
            },
            "body": base64.b64encode(f"name={TEST_GUEST}&email={TEST_GUEST}@example.com".encode()).decode(),
            "isBase64Encoded": True,
        }

        result = lambda_handler(event, None)
        body = json.loads(result["body"])

        success = body["success"]
        error = body["error"]

        clean_up_test_guest(guests_table, "test")

        assert success is not None
        assert error is None
