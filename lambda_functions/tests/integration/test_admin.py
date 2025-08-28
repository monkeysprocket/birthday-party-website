import base64
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from lambda_functions.admin.app.admin import lambda_handler, users_table as app_users_table, \
    guests_table as app_guests_table


@pytest.fixture()
def client_error_users_table():
    with patch.object(app_users_table, "get_item") as mock_get_item:
        mock_get_item.side_effect = ClientError(
            error_response={"Error": {"Message": "Simulated failure"}},
            operation_name="GetItem"
        )
        yield


@pytest.fixture()
def client_error_guests_table():
    with patch.object(app_guests_table, "scan") as mock_get_item:
        mock_get_item.side_effect = ClientError(
            error_response={"Error": {"Message": "Simulated failure"}},
            operation_name="GetItem"
        )
        yield


class TestAdminLambdaHandler:
    def test_success_returns_200(self, user):
        event = {"headers": {"authorization": "Basic " + base64.b64encode(f"{user["username"]}:{user["password"]}".encode()).decode()}}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200

    def test_success_renders_html(self, user):
        event = {"headers": {"authorization": "Basic " + base64.b64encode(f"{user["username"]}:{user["password"]}".encode()).decode()}}

        result = lambda_handler(event, None)

        assert result["body"].startswith("<!DOCTYPE html>")

    def test_success_renders_admin_template(self, user):
        event = {"headers": {"authorization": "Basic " + base64.b64encode(f"{user["username"]}:{user["password"]}".encode()).decode()}}

        result = lambda_handler(event, None)

        assert "Guest RSVP Overview" in result["body"]

    def test_missing_authorization_header_returns_401(self):
        result = lambda_handler({}, None)

        assert result["statusCode"] == 401

    def test_invalid_authorization_scheme_header_returns_401(self):
        event = {"headers": {"authorization": "Not Basic Authorization"}}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 401

    def test_invalid_username_returns_401(self, user):
        event = {"headers": {"authorization": "Basic " + base64.b64encode(f"invalid:{user["password"]}".encode()).decode()}}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 401

    def test_incorrect_password_returns_401(self, user):
        event = {"headers": {"authorization": "Basic " + base64.b64encode(f"{user["username"]}:incorrect".encode()).decode()}}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 401

    def test_dynamodb_error_with_users_table_returns_500(self, user, client_error_users_table):
        event = {"headers": {"authorization": "Basic " + base64.b64encode(f"{user["username"]}:{user["password"]}".encode()).decode()}}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        assert "Simulated failure" in result["body"]

    def test_dynamodb_error_with_guests_table_returns_500(self, user, client_error_guests_table):
        event = {"headers": {"authorization": "Basic " + base64.b64encode(f"{user["username"]}:{user["password"]}".encode()).decode()}}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        assert "Simulated failure" in result["body"]
