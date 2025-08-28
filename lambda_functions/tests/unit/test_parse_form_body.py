import pytest

from lambda_functions.update_guest_rsvp.update_guest_rsvp import parse_form_body, ParsingError


class TestParseFormBody:
    def test_happy_path(self):
        form_body = "uuid=0a1e98250ad64426bea50703ba361477&rsvp=yes&message=test+form+parsing%21"

        uuid, rsvp, message = parse_form_body(raw_body=form_body)

        assert uuid == "0a1e98250ad64426bea50703ba361477"
        assert rsvp == "yes"
        assert message == "test form parsing!"

    def test_empty_message_still_successful(self):
        form_body = "uuid=0a1e98250ad64426bea50703ba361477&rsvp=yes&message="

        uuid, rsvp, message = parse_form_body(raw_body=form_body)

        assert message is None

    @pytest.mark.parametrize(
        "body",
        [
            "rsvp=yes&message=test+form+parsing%21",
            "uuid=0a1e98250ad64426bea50703ba361477&message=",
            "uuid=0a1e98250ad64426bea50703ba361477&rsvp=yes"
        ],
        ids=["missing uuid", "missing rsvp", "missing message"]
    )
    def test_missing_item_raises(self, body):
        with pytest.raises(ParsingError):
            parse_form_body(body)

    def test_malformed_boy_raises(self):
        with pytest.raises(ParsingError):
            parse_form_body(raw_body="dnfkjnfd")
