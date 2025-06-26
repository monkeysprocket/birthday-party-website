import os
import uuid
from pathlib import Path

import boto3
import dotenv
import pytest


@pytest.fixture(scope="session")
def environment():
    env_path = Path(__file__).parent.parent.parent / ".env"
    dotenv.load_dotenv(env_path)

@pytest.fixture(scope="session")
def database(environment):
    dynamodb = boto3.resource('dynamodb')
    dynamodb_table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])
    return dynamodb_table


@pytest.fixture(scope="session")
def guest(database):
    test_guest = {
        "id": uuid.uuid4().hex,
        "name": "alice",
    }
    database.put_item(Item=test_guest)
    yield test_guest
    database.delete_item(Key={"id": test_guest["id"]})
