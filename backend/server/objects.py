from boto3 import resource
from server.database import DYNAMODB_DATABASE_URL
from pydantic import BaseModel, Field
from typing import Union


def get_service_resource():
    return resource("dynamodb", endpoint_url=DYNAMODB_DATABASE_URL)


class Attribute(Field):
    """
    A field that represents a DynamoDB Attribute.
    An Attribute Name must be a String and have a minimum length of 1 characters and a maximum length of 255 characters.
    An Attribute Value must be either a String, Number, or Binary.
    """

    @staticmethod
    def validate(key: str, value: Union[str, int, float, bytes]):
        if not isinstance(key, str):
            raise TypeError(f"Attribute Name must be a String, not {type(key)}")
        if not isinstance(value, (str, int, float, bytes)):
            raise TypeError(
                f"Attribute Value must be either a String, Number, or Binary, not {type(value)}"
            )
        if len(key) < 1 or len(key) > 255:
            raise ValueError(
                f"Attribute Name must have a minimum length of 1 characters and a maximum length of 255 characters, not {len(key)}"
            )


class DDBTable(BaseModel):
    __tablename__: str
    __table_class__: str = "STANDARD"


class Workflows:
    __tablename__ = "workflows"
    __schema__ = dict(
        AttributeDefinitions=[
            {"AttributeName": "string", "AttributeType": "S" | "N" | "B"},
        ],
        TableName=__tablename__,
        KeySchema=[
            {"AttributeName": "string", "KeyType": "HASH" | "RANGE"},
        ],
        LocalSecondaryIndexes=[
            {
                "IndexName": "string",
                "KeySchema": [
                    {"AttributeName": "string", "KeyType": "HASH" | "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL" | "KEYS_ONLY" | "INCLUDE",
                    "NonKeyAttributes": [
                        "string",
                    ],
                },
            },
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "string",
                "KeySchema": [
                    {"AttributeName": "string", "KeyType": "HASH" | "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL" | "KEYS_ONLY" | "INCLUDE",
                    "NonKeyAttributes": [
                        "string",
                    ],
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 123,
                    "WriteCapacityUnits": 123,
                },
            },
        ],
        BillingMode="PROVISIONED" | "PAY_PER_REQUEST",
        ProvisionedThroughput={"ReadCapacityUnits": 123, "WriteCapacityUnits": 123},
        StreamSpecification={
            "StreamEnabled": True | False,
            "StreamViewType": "NEW_IMAGE"
            | "OLD_IMAGE"
            | "NEW_AND_OLD_IMAGES"
            | "KEYS_ONLY",
        },
        SSESpecification={
            "Enabled": True | False,
            "SSEType": "AES256" | "KMS",
            "KMSMasterKeyId": "string",
        },
        Tags=[
            {"Key": "string", "Value": "string"},
        ],
        TableClass="STANDARD" | "STANDARD_INFREQUENT_ACCESS",
        DeletionProtectionEnabled=True | False,
    )

    def __init__(self, service_resource) -> None:
        self.service_resource = service_resource
        print(self.service_resource.tables.all())


Workflows(get_service_resource())
