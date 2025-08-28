import base64

import pytest

from lambda_functions.admin.app.auth_header_parsing import get_username_and_password_from_basic_auth_header, AuthHeaderParsingError

USERNAME = "admin"
PASSWORD = "supersecret"

class TestGetUsernameAndPassword:
    def test_username_extracted(self):
        auth_header = "Basic " + base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
        result, _ = get_username_and_password_from_basic_auth_header(auth_header)

        assert result == USERNAME

    def test_password_extracted(self):
        auth_header = "Basic " + base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
        _, result = get_username_and_password_from_basic_auth_header(auth_header)

        assert result == PASSWORD

    @pytest.mark.parametrize(
        "auth_header",
        ["dnkjasndkjadns", "dfbndkjsnf kjnsda", "Basic " + base64.b64encode("dnsfkjsdf".encode()).decode()],
        ids=["random str", "with space", "without colon"]
    )
    def test_malformed_header_raises(self, auth_header: str):
        with pytest.raises(AuthHeaderParsingError):
            get_username_and_password_from_basic_auth_header(auth_header)