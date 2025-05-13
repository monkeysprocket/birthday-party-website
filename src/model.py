import os
from uuid import UUID, uuid4

import boto3
from botocore.exceptions import ClientError

from .exceptions import IncompleteDataError


class Model:
    def __init__(self) -> None:
        self._dynamodb = boto3.resource("dynamodb", region_name=os.environ['AWS_REGION'])
        self._guests_table = self._dynamodb.Table("guests")
        self._users_table = self._dynamodb.Table("users")
    
    def get_all_guests(self):
        response = self._guests_table.scan(
            ProjectionExpression="#n, email, rsvp_status, rsvp_message",
            ExpressionAttributeNames={"#n": "name"},
        )
        return [
            (item["name"], item["email"], item.get("rsvp_status", "pending"), item.get("rsvp_message", ""))
            for item in response.get("Items", [])
        ]

    def add_guest(self, name: str, email: str) -> str:
        if not name or not email:
            raise IncompleteDataError

        new_guest_uuid = uuid4().hex
        item = {
            "id": new_guest_uuid,
            "name": name,
            "email": email,
            "rsvp_status": "pending"
        }

        try:
            self._guests_table.put_item(Item=item, ConditionExpression="attribute_not_exists(email)")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ValueError("Guest with this email already exists.")
            else:
                raise
        return new_guest_uuid
    
    def update_guest_rsvp(self, uuid: UUID, rsvp: str, message: str) -> None:
        try:
            self._guests_table.update_item(
                Key={"id": str(uuid)},
                UpdateExpression="SET rsvp_status = :r, rsvp_message = :m",
                ExpressionAttributeValues={
                    ":r": rsvp,
                    ":m": message
                }
            )
        except ClientError as e:
            raise RuntimeError(e.response['Error']['Message'])


if __name__ == "__main__":
    model = Model()
    print(model.get_all_guests())