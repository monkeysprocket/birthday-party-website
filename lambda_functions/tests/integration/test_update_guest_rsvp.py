import json
import uuid
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from lambda_functions.update_guest_rsvp.app import lambda_handler, dynamodb_table


@pytest.fixture()
def client_error():
    with patch.object(dynamodb_table, "update_item") as mock_get_item:
        mock_get_item.side_effect = ClientError(
            error_response={"Error": {"Message": "Simulated failure"}},
            operation_name="GetItem"
        )
        yield


class TestLambdaHandler:
    def test_guest_exists(self, guest):
        event = {"body": json.dumps({"uuid": guest["id"], "rsvp": "yes", "message": ""})}
        print(event)

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        assert "OK" in result["body"]

    def test_guest_does_not_exist_returns_500(self):
        event = {"body": json.dumps({"uuid": uuid.uuid4().hex, "rsvp": "yes", "message": ""})}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        assert "UpdateItem failed: guest uuid not found" in result["body"]

    def test_client_error_returns_500(self, guest, client_error):
        event = {"body": json.dumps({"uuid": guest["id"], "rsvp": "yes", "message": ""})}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        assert "Simulated failure" in result["body"]

    def test_input_validation_uuid_missing_returns_400(self):
        event = {"body": json.dumps({"rsvp": "yes", "message": ""})}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "Missing 'uuid'" in result["body"]

    def test_input_validation_rsvp_missing_returns_400(self):
        event = {"body": json.dumps({"uuid": uuid.uuid4().hex, "message": ""})}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "Missing 'rsvp'" in result["body"]

    def test_input_validation_message_missing_returns_200(self, guest):
        event = {"body": json.dumps({"uuid": guest["id"], "rsvp": "yes"})}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200

    def test_input_validation_malformed_json_returns_400(self):
        event = {"body": "{"}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "Invalid JSON in request body" in result["body"]
