from lambda_functions.index.index import lambda_handler


class TestIndexLambdaHandler:
    def test_success_returns_200(self):
        result = lambda_handler()

        assert result["statusCode"] == 200

    def test_success_renders_html(self):
        result = lambda_handler()

        assert result["body"].startswith("<!DOCTYPE html>")

    def test_success_renders_index_template(self):
        result = lambda_handler()

        assert "A simple app for sending and managing party invitations." in result["body"]
