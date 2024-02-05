import sys
from boto3 import resource
from boto3.dynamodb.conditions import Key, Attr
from pprint import pprint
from dataclasses import dataclass
from server.database import DYNAMODB_DATABASE_URL
from pydantic import BaseModel
from pydantic.fields import FieldInfo, Field
from logging import getLogger, StreamHandler
from shortuuid import uuid
from inspect import isclass
from server.utils import get_literals_from_regex
from typing import (
    Any,
    Type,
    Annotated,
    Union,
    ParamSpec,
    TypeVar,
    ClassVar,
    Literal,
    TypedDict,
    List,
)

# TYPES #
Param = ParamSpec("Param")
RetType = TypeVar("RetType")
KeySortType = Literal["HASH", "RANGE"]
KeyAttributeType = Literal["B", "S", "N"]
BillingModeType = Literal["PROVISIONED", "PAY_PER_REQUEST"]
SelectType = Literal[
    "ALL_ATTRIBUTES", "ALL_PROJECTED_ATTRIBUTES", "COUNT", "SPECIFIC_ATTRIBUTES"
]

logger = getLogger(__name__)
logger.addHandler(StreamHandler(sys.stdout))
logger.setLevel("INFO")


class KeySchemaElementType(TypedDict):
    AttributeName: str
    KeyType: KeySortType


class AttributeDefinitionsElementType(TypedDict):
    AttributeName: str
    AttributeType: KeyAttributeType


def get_service_resource():
    return resource("dynamodb", endpoint_url=DYNAMODB_DATABASE_URL)


@dataclass
class Attribute:
    name: str
    type: KeyAttributeType


@dataclass
class PartitionKey(Attribute):
    sort: KeySortType = "HASH"


@dataclass
class SortKey(Attribute):
    sort: KeySortType = "RANGE"


class Item(BaseModel):
    __table__: "Table | None" = None

    def put(self):
        assert self.__table__ is not None, "You must define a table for this item"
        assert self.__table__.put_item(self.model_dump())

    @classmethod
    def scan(
        cls,
        limit: int | None = None,
        index_name: str | None = None,
        start_key: str | None = None,
    ):
        assert cls.__table__ is not None, "You must define a table for this item"
        projection = cls.model_fields.keys()
        projection_attribute_names = {f"#x{i}": x for i, x in enumerate(projection)}
        projection_expression = ", ".join(projection_attribute_names.keys())
        pk = cls.__table__._get_partition_key()
        sk = cls.__table__._get_sort_key()
        conditions = cls._get_key_constraints(pk.name, cls.model_fields[pk.name])
        if sk:
            conditions.extend(
                cls._get_key_constraints(sk.name, cls.model_fields[sk.name])
            )
        expression = cls._get_expression(conditions)

        # fmt: off
        params: dict[str, Any] = {k: v for k, v in {
            "Limit": limit,
            "IndexName": index_name,
            "FilterExpression": expression,
            "ExclusiveStartKey" : start_key
            }.items() if v is not None
        }

        return cls.__table__.table.scan(
            Select="SPECIFIC_ATTRIBUTES", 
            ProjectionExpression=projection_expression,
            ExpressionAttributeNames=projection_attribute_names,
            **params,
        )

    @staticmethod
    def _get_expression(conditions: list[Key]) -> None | Key:
        if conditions:
            expression = conditions[0]
            for condition in conditions[1:]:
                expression = expression & condition
            return expression
        else:
            return None

    @staticmethod
    def _get_key_constraints(key, info: FieldInfo) -> list[Key]:
        conditions = []
        for metadata in info.metadata:
            if hasattr(metadata, "pattern"):
                literals = get_literals_from_regex(metadata.pattern)
                if literals.startswith:
                    conditions.append(Key(key).begins_with(literals.startswith))
        return conditions


class Table:
    __tablename__: str
    __billing_mode__: BillingModeType = "PAY_PER_REQUEST"
    __item_schema__: type[BaseModel] = BaseModel
    Name = Attribute("Name", "S")
    _ItemType = TypeVar("_ItemType", __item_schema__, BaseModel)

    def __init__(self) -> None:
        self.resource = get_service_resource()
        self._deleted = False
        if not self.exists:
            logger.info(f"Creating new table: {self.__tablename__}")
            self._table = self.create_table()
        else:
            logger.info(f"Using existing table: {self.__tablename__}")
            self._table = self.resource.Table(self.__tablename__)
        self._apply_table_to_items()

    def create_table(self):
        return self.resource.create_table(
            TableName=self.__tablename__,
            KeySchema=self.key_schema,
            AttributeDefinitions=self.attribute_definitions,
            BillingMode=self.__billing_mode__,
        )

    def scan(
        self,
        select: SelectType = "ALL_ATTRIBUTES",
        limit: int | None = None,
        index_name: str | None = None,
    ):
        params = {
            k: v
            for k, v in {
                "Select": select,
                "Limit": limit,
                "IndexName": index_name,
            }.items()
            if v
        }
        return self.table.scan(**params)

    def delete(self):
        logger.info(f"Deleting table: {self.__tablename__}")
        self.table.delete()
        self._deleted = True

    def put_item(self, item: dict):
        return self.table.put_item(Item=item)

    def _get_partition_key(self) -> PartitionKey:
        keys = [
            x for x in self.__class__.__dict__.values() if isinstance(x, PartitionKey)
        ]
        assert len(keys) == 1, "You must define exactly one PartitionKey"
        return keys[0]

    def _get_sort_key(self) -> Union[SortKey, None]:
        keys = [x for x in self.__class__.__dict__.values() if isinstance(x, SortKey)]
        assert len(keys) <= 1, "You cannot define more than one SortKey"
        return keys[0] if keys else None

    def _get_attributes(self) -> List[Attribute]:
        return [x for x in self.__class__.__dict__.values() if isinstance(x, Attribute)]

    def _apply_table_to_items(self):
        for item in [
            x
            for x in self.__class__.__dict__.values()
            if isclass(x) and issubclass(x, Item)
        ]:
            item.__table__ = self

    @property
    def key_schema(self) -> List[KeySchemaElementType]:
        partition_key = self._get_partition_key()
        sort_key = self._get_sort_key()
        schema: List[KeySchemaElementType] = [
            {"AttributeName": partition_key.name, "KeyType": partition_key.sort},
        ]
        if sort_key:
            schema.append({"AttributeName": sort_key.name, "KeyType": sort_key.sort})
        return schema

    @property
    def attribute_definitions(self) -> List[AttributeDefinitionsElementType]:
        return [
            {"AttributeName": x.name, "AttributeType": x.type}
            for x in self._get_attributes()
        ]

    @property
    def table(self):
        assert not self._deleted, "This table has been deleted"
        assert self._table, "Table does not exist"
        return self._table

    @property
    def exists(self) -> bool:
        for table in self.resource.tables.all():
            if table.name == self.__tablename__:
                return True
        return False


_WorkflowID = Field(
    pattern=r"Workflow\-[a-zA-Z0-9]*",
    default_factory=lambda: f"Workflow-{uuid()}",
    validate_default=True,
    alias="WorkflowID",
)
_NodeID = Field(
    pattern=r"Node\-[a-zA-Z0-9]*",
    default_factory=lambda: f"Node-{uuid()}",
    validate_default=True,
    alias="NodeID",
)

_EdgeID = Field(
    pattern=r"Edge\-[a-zA-Z0-9]*",
    default_factory=lambda: f"Edge-{uuid()}",
    validate_default=True,
    alias="EdgeID",
)


class Workflows(Table):
    __tablename__ = "Workflows"
    __billing_mode__ = "PAY_PER_REQUEST"
    partition_key = PartitionKey("PartitionKey", "S")
    sort_key = SortKey("SortKey", "S")

    class Workflow(Item):
        PartitionKey: str = _WorkflowID
        SortKey: str = _WorkflowID
        Name: str
        ID: str
        Owner: str

    class Node(Item):
        PartitionKey: str = _WorkflowID
        SortKey: str = _NodeID
        ID: str
        Version: str
        Manifest: List[Annotated[str, _NodeID]] = []
        Node: str

    class Edge(Item):
        PartitionKey: str = _WorkflowID
        SortKey: str = _EdgeID
        From: str
        To: str


if __name__ == "__main__":
    from pprint import pprint

    workflows = Workflows()
    print('Get All Workflows')
    pprint(workflows.Workflow.scan())

    print('Get All Nodes')
    pprint(workflows.Node.scan())

    print('Get All Edges')
    pprint(workflows.Edge.scan())
    
