from contextlib import contextmanager
from decimal import Decimal
import json
from lib2to3.fixes.fix_idioms import TYPE
import sys
from boto3 import resource
from boto3.dynamodb.conditions import Key, Attr, And, Or, Equals, NotEquals, BeginsWith
from dataclasses import dataclass
from pydantic import BaseModel, TypeAdapter, ConfigDict, ValidationError
from pydantic.fields import FieldInfo, Field, computed_field
from logging import getLogger, StreamHandler
from shortuuid import uuid
from inspect import isclass
from server.utils import get_literals_from_regex
from functools import lru_cache
from typing import (
    Generator,
    Generic,
    Self,
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
    Type,
    overload,
)

DYNAMODB_DATABASE_URL = "http://localhost:8000"

# TYPES #
OperatorClasses = Union[
    Type[And], Type[Or], Type[Equals], Type[NotEquals], Type[BeginsWith]
]
Operators = Union[And, Or, Equals, NotEquals, BeginsWith]
Selections = Literal[
    "ALL_ATTRIBUTES", "ALL_PROJECTED_ATTRIBUTES", "COUNT", "SPECIFIC_ATTRIBUTES"
]


class Boto3ResponseMetadata(TypedDict):
    RequestID: str
    HTTPStatusCode: int
    HTTPHeaders: dict[str, str]
    RetryAttempts: int


T = TypeVar("T")


class Boto3QueryResponseType(TypedDict):
    Count: int
    ScannedCount: int
    Items: list[dict[str, Any]]
    ResponseMetadata: Boto3ResponseMetadata


Param = ParamSpec("Param")
RetType = TypeVar("RetType")
KeySortType = Literal["HASH", "RANGE"]
KeyAttributeType = Literal["B", "S", "N"]
BillingModeType = Literal["PROVISIONED", "PAY_PER_REQUEST"]
SelectType = Literal[
    "ALL_ATTRIBUTES", "ALL_PROJECTED_ATTRIBUTES", "COUNT", "SPECIFIC_ATTRIBUTES"
]

logger = getLogger("server.database")


class KeySchemaElementType(TypedDict):
    AttributeName: str
    KeyType: KeySortType


class AttributeDefinitionsElementType(TypedDict):
    AttributeName: str
    AttributeType: KeyAttributeType


@lru_cache
def get_service_resource():
    return resource("dynamodb", endpoint_url=DYNAMODB_DATABASE_URL)


@lru_cache
def _table_exists(table_name: str) -> bool:
    resource = get_service_resource()
    for table in resource.tables.all():
        if table.name == table_name:
            return True
    return False


def _cache_clear():
    _table_exists.cache_clear()
    get_service_resource.cache_clear()


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

    model_config = ConfigDict(
        populate_by_name=True,
    )

    def put(self):
        assert self.__table__ is not None, "You must define a table for this item"
        self.__table__.put_item(self.model_dump())

    #    @classmethod
    #    def delete(cls, key: str | int, sort_key: str | int | None = None):
    #        assert cls.__table__ is not None, "You must define a table for this item"
    #        pk = cls.__table__._get_partition_key()
    #        sk = cls.__table__._get_sort_key()
    #        cls._validate_field_value(pk.name, key)
    #        key_dict = {cls.__table__._get_partition_key().name: key}
    #        if sk:
    #            cls._validate_field_value(sk.name, sort_key)
    #            key_dict[cls.__table__._get_sort_key().name] = sort_key # type: ignore
    #        response=cls.__table__.table.delete_item(Key=key_dict, ReturnValues="ALL_OLD")
    #        return response
    def delete(self):
        assert self.__table__ is not None, "You must define a table for this item"
        pk = self.__table__._get_partition_key()
        sk = self.__table__._get_sort_key()
        key_dict = {pk.name: getattr(self, pk.name)}
        if sk:
            key_dict[sk.name] = getattr(self, sk.name)
        response = self.__table__.table.delete_item(
            Key=key_dict, ReturnValues="ALL_OLD"
        )
        return response

    @classmethod
    def _validate_field_value(cls, field_name: str, value):
        cls.__pydantic_validator__.validate_assignment(
            cls.model_construct(), field_name, value
        )

    @classmethod
    def _get_projection_expression(cls) -> tuple[str, dict[str, str]]:
        projection = cls.model_fields.keys()
        projection_attribute_names = {f"#x{i}": x for i, x in enumerate(projection)}
        projection_expression = ", ".join(projection_attribute_names.keys())
        return projection_expression, projection_attribute_names

    @classmethod
    def get(cls, key: str | int, sort_key: str | int | None = None) -> Self | None:
        assert cls.__table__ is not None, "You must define a table for this item"
        (
            projection_expression,
            projection_attribute_names,
        ) = cls._get_projection_expression()
        pk = cls.__table__._get_partition_key()
        sk = cls.__table__._get_sort_key()
        cls._validate_field_value(pk.name, key)
        exp = Key(pk.name).eq(key)
        if sk:
            cls._validate_field_value(sk.name, sort_key)
            exp = exp & Key(sk.name).eq(sort_key)

        response: Boto3QueryResponseType = cls.__table__.table.query(
            KeyConditionExpression=exp,
            Select="SPECIFIC_ATTRIBUTES",
            ProjectionExpression=projection_expression,
            ExpressionAttributeNames=projection_attribute_names,
        )
        assert (
            response["Count"] <= 1
        ), f"Multiplicity Error: The keys: PK:{key}, SK:{sort_key} are not unique"

        if response["Count"] == 0:
            return None
        else:
            return cls(**response["Items"][0])

    @classmethod
    def _filter(
        cls, items: list[dict], raise_validation_error: bool = False
    ) -> list[Self]:
        filtered: list[Self] = []
        for item in items:
            try:
                filtered.append(cls(**item))
            except ValidationError as e:
                if raise_validation_error:
                    raise
        return filtered

    @classmethod
    def query(
        cls,
        key: str | int,
        key_expression: Key | Operators | None = None,
        key_operator: OperatorClasses = And,
        filter: bool = True,
    ) -> "QueryResponse[Self]":
        assert cls.__table__ is not None, "You must define a table for this item"
        (
            projection_expression,
            projection_attribute_names,
        ) = cls._get_projection_expression()
        pk = cls.__table__._get_partition_key()
        sk = cls.__table__._get_sort_key()
        cls._validate_field_value(pk.name, key)
        exp = Key(pk.name).eq(key)

        if key_expression:
            exp = key_operator(exp, key_expression)

        response: Boto3QueryResponseType = cls.__table__.query(  # type: ignore
            key_condition_expression=exp,
            select="SPECIFIC_ATTRIBUTES",
            projection_expression=projection_expression,
            expression_attribute_names=projection_attribute_names,
            raw=True,
        )
        return QueryResponse(
            Count=response.get("Count"),
            ScannedCount=response.get("ScannedCount"),
            Items=cls._filter(response["Items"], raise_validation_error=not filter),
            ResponseMetadata=response.get("ResponseMetadata"),
        )

    @classmethod
    def scan(
        cls,
        limit: int | None = None,
        index_name: str | None = None,
        start_key: str | None = None,
        filter: bool = True,
    ) -> "QueryResponse[Self]":
        assert cls.__table__ is not None, "You must define a table for this item"
        (
            projection_expression,
            projection_attribute_names,
        ) = cls._get_projection_expression()
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
        # fmt: on

        items = cls.__table__.table.scan(
            Select="SPECIFIC_ATTRIBUTES",
            ProjectionExpression=projection_expression,
            ExpressionAttributeNames=projection_attribute_names,
            **params,
        )
        items["Items"] = cls._filter(items["Items"], not filter)
        return QueryResponse(**items)

    @staticmethod
    def _get_expression(conditions: list[Key | Operators]) -> None | Key | Operators:
        if conditions:
            expression = conditions[0]
            for condition in conditions[1:]:
                expression = expression & condition
            return expression
        else:
            return None

    @staticmethod
    def _get_key_constraints(key, info: FieldInfo) -> list[Key | Operators]:
        conditions = []
        for metadata in info.metadata:
            if hasattr(metadata, "pattern"):
                literals = get_literals_from_regex(metadata.pattern)
                if literals.startswith:
                    conditions.append(Key(key).begins_with(literals.startswith))
        return conditions


class QueryResponse(Generic[T]):
    def __init__(
        self,
        Items: List[T],
        ScannedCount: int,
        Count: int,
        ResponseMetadata: Boto3ResponseMetadata,
    ) -> None:
        self.items: List[T] = Items
        self.scanned_count: int = ScannedCount
        self.count: int = Count
        self.response_metadata: Boto3ResponseMetadata = ResponseMetadata


def _convert_base_model(func):
    def wrapper(*args, **kwargs):
        new_args = [
            (
                json.loads(x.model_dump_json(), parse_float=Decimal)
                if isinstance(x, BaseModel)
                else x
            )
            for x in args
        ]
        new_kwargs = {
            k: (
                json.loads(v.model_dump_json(), parse_float=Decimal)
                if isinstance(v, BaseModel)
                else v
            )
            for k, v in kwargs.items()
        }
        return func(*new_args, **new_kwargs)

    return wrapper


class Table:
    __tablename__: str
    __billing_mode__: BillingModeType = "PAY_PER_REQUEST"
    __item_schema__: type[BaseModel] = BaseModel
    Name = Attribute("Name", "S")
    _ItemType = TypeVar("_ItemType", __item_schema__, BaseModel)

    def __init__(self) -> None:
        self.resource = get_service_resource()
        self._deleted = False
        if not _table_exists(self.__tablename__) and not (
            _cache_clear() or _table_exists(self.__tablename__)
        ):
            try:
                logger.info(f"Creating new table: {self.__tablename__}")
                self._table = self.create_table()
            finally:
                _cache_clear()
        else:
            self._table = self.resource.Table(self.__tablename__)
        self._apply_table_to_items()

    @contextmanager
    def batch_writer(self):
        with self._table.batch_writer() as batch:
            batch.put_item = _convert_base_model(batch.put_item)
            batch.delete_item = _convert_base_model(batch.delete_item)
            yield batch

    @classmethod
    def items(cls) -> Generator[tuple[str, Type[Item]], None, None]:
        for attr in dir(cls):
            if not attr.startswith("_"):
                obj = getattr(cls, attr)
                if isclass(obj) and issubclass(obj, Item):
                    yield attr, obj

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
        raw: bool = False,
    ) -> Boto3QueryResponseType | QueryResponse[Item]:
        params = {
            k: v
            for k, v in {
                "Select": select,
                "Limit": limit,
                "IndexName": index_name,
            }.items()
            if v
        }
        response: Boto3QueryResponseType = self.table.scan(**params)
        if raw:
            return response
        else:
            return self._get_query_response_from_boto3_response(response)

    def query(
        self,
        key_condition_expression: Key | Operators | None,
        select: Selections = "ALL_ATTRIBUTES",
        projection_expression: str | None = None,
        expression_attribute_names: dict[str, str] | None = None,
        scan_index_forward: bool = True,
        limit: int | None = None,
        index_name: str | None = None,
        exclusive_start_key: dict[str, Any] | None = None,
        raw: bool = False,
    ) -> QueryResponse[Item]:

        params = dict(
            ProjectionExpression=projection_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ScanIndexForward=scan_index_forward,
            Limit=limit,
            IndexName=index_name,
            ExclusiveStartKey=exclusive_start_key,
        )
        params = {k: v for k, v in params.items() if v is not None}
        response: Boto3QueryResponseType = self.table.query(
            KeyConditionExpression=key_condition_expression,
            Select=select,
            **params,
        )
        if raw:
            return response  # type: ignore
        else:
            return self._get_query_response_from_boto3_response(response)

    def delete(self):
        logger.info(f"Deleting table: {self.__tablename__}")
        self.table.delete()
        self._deleted = True

    def put_item(self, item: dict):
        return self.table.put_item(Item=item)

    @classmethod
    def _get_query_response_from_boto3_response(
        cls, response: Boto3QueryResponseType
    ) -> QueryResponse[Item]:
        for i, item in enumerate(response["Items"]):
            for key, Item in cls.items():
                try:
                    response["Items"][i] = Item(**item)  # type: ignore
                    break
                except ValidationError as e:
                    pass
            else:
                raise ValueError(f"Cannot infer item type for : {item}")
        return QueryResponse(**response)  # type: ignore

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
