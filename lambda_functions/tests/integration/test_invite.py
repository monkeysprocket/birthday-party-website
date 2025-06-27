from unittest.mock import patch
from uuid import uuid4

import pytest
from botocore.exceptions import ClientError

from lambda_functions.invite.invite import lambda_handler, users_table


@pytest.fixture()
def client_error():
    with patch.object(users_table, "get_item") as mock_get_item:
        mock_get_item.side_effect = ClientError(
            error_response={"Error": {"Message": "Simulated failure"}},
            operation_name="GetItem"
        )
        yield


class TestIndexLambdaHandler:
    def test_success_returns_200(self, guest):
        event = {"pathParameters": {"uuid": guest["id"]}, "queryStringParameters": None}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200

    def test_success_renders_html(self, guest):
        event = {"pathParameters": {"uuid": guest["id"]}, "queryStringParameters": None}

        result = lambda_handler(event, None)

        assert result["body"].startswith("<!DOCTYPE html>")

    def test_success_renders_invite_template(self, guest):
        event = {"pathParameters": {"uuid": guest["id"]}, "queryStringParameters": None}

        result = lambda_handler(event, None)

        assert "You're Invited to a Birthday Party!" in result["body"]

    def test_missing_uuid_path_parameter_returns_400(self):
        event = {"queryStringParameters": None}  # no "uuid" key
        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "Missing 'uuid'" in result["body"]

    def test_dynamodb_error_returns_500(self, guest, client_error):
        event = {"pathParameters": {"uuid": guest["id"]}, "queryStringParameters": None}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        assert "Simulated failure" in result["body"]

    def test_guest_does_not_exist_returns_404(self):
        event = {"pathParameters": {"uuid": uuid4().hex}, "queryStringParameters": None}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 404
        assert "Guest not found" in result["body"]

    def test_rsvp_query_parameter_true_reveals_thank_you_message(self, guest):
        event = {"pathParameters": {"uuid": guest["id"]}, "queryStringParameters": {"rsvp_thanks": True}}

        result = lambda_handler(event, None)

        assert "we've saved your RSVP!" in result["body"]

    def test_rsvp_query_parameter_false_hides_thank_you_message(self, guest):
        event = {"pathParameters": {"uuid": guest["id"]}, "queryStringParameters": {"rsvp_thanks": False}}

        result = lambda_handler(event, None)

        assert "we've saved your RSVP!" not in result["body"]

    def test_rsvp_query_parameter_missing_hides_thank_you_message(self, guest):
        event = {"pathParameters": {"uuid": guest["id"]}, "queryStringParameters": None}

        result = lambda_handler(event, None)

        assert "we've saved your RSVP!" not in result["body"]
