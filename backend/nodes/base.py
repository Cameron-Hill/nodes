from nodes.errors import UnhandledNodeError
from abc import ABC, abstractmethod
from pydantic_core import ValidationError, core_schema
from typing_extensions import get_args
from pydantic import BaseModel, GetCoreSchemaHandler, ValidationInfo
from pydantic.fields import FieldInfo
from typing import Generic, TypeVar, Any

T = TypeVar("T")


class NodeSchema(BaseModel):
    """This class represents the schema for a node."""

    id: str
    label: str
    group: str | None
    sub_group: str | None
    version: int
    input: dict | None
    output: dict | None
    options: dict | None


class Node(ABC):
    """"""

    __group__: str = None
    __sub_group__: str = None
    __label__: str = None
    __version__: int = 0

    def __repr__(self) -> str:
        return self.id()

    @classmethod
    def id(cls):
        return f"{cls.__module__}.{cls.__name__}"

    @classmethod
    def label(cls):
        return cls.__label__ or cls.__name__

    @abstractmethod
    def run(self, input: BaseModel | None, options: BaseModel | None):
        """This method is called when the node is run. It is passed the input
        data and should return a dict that will be passed to the next node."""
        raise NotImplementedError

    def error_handler(self, exception: Exception):
        """This method is called when an exception is raised in a node. It is
        passed the exception that was raised and should return a dict that
        will be returned to the user as the result of the node."""
        raise UnhandledNodeError(
            f"Unhandled exception in node {self._label}: {exception}"
        ) from exception

    @classmethod
    def node_json_schema(cls) -> NodeSchema:
        """Return the schema for the node."""
        input_schema = cls.run.__annotations__.get("input")
        output_schema = cls.run.__annotations__.get("return")
        options_schema = cls.Options if hasattr(cls, "Options") else None

        return NodeSchema(
            id=cls.id(),
            label=cls.label(),
            group=cls.__group__,
            sub_group=cls.__sub_group__,
            version=cls.__version__,
            input=input_schema.model_json_schema() if input_schema else None,
            output=output_schema.model_json_schema() if output_schema else None,
            options=options_schema.model_json_schema() if options_schema else None,
        )


class Option(Generic[T]):
    """This class represents an option that can be passed to a node."""

    def __init__(
        self, value: T, name: str | None = None, field_info: FieldInfo | None = None
    ):
        self.value = value
        self.name = name
        self.field_info = field_info

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        instance_schema = core_schema.is_instance_schema(cls)

        args = get_args(source)
        try:
            generic_t_schema = handler.generate_schema(args[0])
        except IndexError:
            raise ValidationError(
                [
                    ValidationInfo(
                        cls,
                        source,
                        "Option annotation must have a type argument e.g. Option[int]",
                    )
                ]
            )

        non_instance_schema = core_schema.no_info_after_validator_function(
            Option, generic_t_schema
        )
        return core_schema.union_schema([instance_schema, non_instance_schema])


class NodeSource(ABC):
    """"""

    def __init__(self, source: str) -> None:
        self.source: str = source
        self.nodes: set[Node] = set()
        self.resolve_nodes()

    @abstractmethod
    def resolve_nodes(self) -> set[Node]:
        raise NotImplementedError

    def add(self, node: Node):
        if node in self.nodes:
            raise ValueError(f"Node {node} already exists in source {self.source}")
        self.nodes.add(node)
