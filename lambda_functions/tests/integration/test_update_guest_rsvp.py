from unittest.mock import patch
from uuid import uuid4

import pytest
from botocore.exceptions import ClientError

from lambda_functions.update_guest_rsvp.update_guest_rsvp import lambda_handler, dynamodb_table


@pytest.fixture()
def client_error():
    with patch.object(dynamodb_table, "update_item") as mock_get_item:
        mock_get_item.side_effect = ClientError(
            error_response={"Error": {"Message": "Simulated failure"}},
            operation_name="GetItem"
        )
        yield


class TestLambdaHandler:
    def test_successful_update(self, guest, database):
        unique_message = uuid4().hex
        event = {"body": f"uuid={guest["id"]}&rsvp=yes&message={unique_message}"}

        lambda_handler(event, None)

        item = database.get_item(Key={"id": guest["id"]}).get("Item")

        assert item["rsvp_message"] == unique_message

    def test_successful_update_redirects(self, guest):
        event = {"body": f"uuid={guest["id"]}&rsvp=yes&message="}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 301

    def test_form_parsing_error_returns_400(self, guest):
        event = {"body": f"uuid={guest["id"]}&message="}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "Failed to parse application/x-www-form-urlencoded data" in result["body"]

    def test_guest_does_not_exist_returns_400(self):
        event = {"body": f"uuid={uuid4().hex}&rsvp=yes&message="}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "UpdateItem failed: guest uuid not found" in result["body"]

    def test_client_error_returns_500(self, guest, client_error):
        event = {"body": f"uuid={guest["id"]}&rsvp=yes&message="}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        assert "Simulated failure" in result["body"]


    def test_parsing_error_returns_400(self):
        event = {"body": "dfsdfs"}  # will raise a ParsingError

        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "Failed to parse application/x-www-form-urlencoded data" in result["body"]
