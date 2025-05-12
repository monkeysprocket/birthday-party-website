import uuid
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from lambda_functions.get_guest_name_from_invite_uuid.app import dynamodb_table


@pytest.fixture(scope="module")
def guest():
    test_guest = {
        "id": uuid.uuid4().hex,
        "name": "alice",
    }
    dynamodb_table.put_item(Item=test_guest)
    yield test_guest
    dynamodb_table.delete_item(Key={"id": test_guest["id"]})

@pytest.fixture()
def client_error():
    with patch.object(dynamodb_table, "get_item") as mock_get_item:
        mock_get_item.side_effect = ClientError(
            error_response={"Error": {"Message": "Simulated failure"}},
            operation_name="GetItem"
        )
        yield
