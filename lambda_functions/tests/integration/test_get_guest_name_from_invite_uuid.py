import uuid

from lambda_functions.get_guest_name_from_invite_uuid.app import lambda_handler


class TestLambdaHandler:
    def test_guest_exists(self, guest):
        event = {"uuid": guest["id"]}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        assert guest["name"] in result["body"]

    def test_guest_does_not_exist(self):
        event = {"uuid": uuid.uuid4().hex}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 404
        assert "Guest not found" in result["body"]

    def test_input_validation(self, guest):
        event = {}  # no "uuid" key
        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "Missing 'uuid'" in result["body"]

    def test_dynamodb_failure(self, guest, client_error):
        event = {"uuid": guest["id"]}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        assert "Simulated failure" in result["body"]
