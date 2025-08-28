import os
import uuid
from pathlib import Path

import boto3
import dotenv
import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="session")
def environment():
    env_path = Path(__file__).parent.parent.parent / ".env"
    dotenv.load_dotenv(env_path)

@pytest.fixture(scope="session")
def guests_table(environment):
    dynamodb = boto3.resource('dynamodb')
    dynamodb_table = dynamodb.Table(os.environ["DYNAMODB_GUESTS_TABLE"])
    return dynamodb_table


@pytest.fixture(scope="session")
def guest(guests_table):
    test_guest = {
        "id": uuid.uuid4().hex,
        "name": "alice",
    }
    guests_table.put_item(Item=test_guest)
    yield test_guest
    guests_table.delete_item(Key={"id": test_guest["id"]})


@pytest.fixture(scope="session")
def users_table(environment):
    dynamodb = boto3.resource('dynamodb')
    dynamodb_table = dynamodb.Table(os.environ["DYNAMODB_USERS_TABLE"])
    return dynamodb_table


@pytest.fixture(scope="session")
def user(users_table):
    test_user = {
        "username": "test_user",
        "password_hash": generate_password_hash("supersecret"),
    }
    users_table.put_item(Item=test_user)
    test_user["password"] = "supersecret"
    yield test_user
    users_table.delete_item(Key={"username": test_user["username"]})
