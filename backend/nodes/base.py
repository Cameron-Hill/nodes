from nodes.errors import UnhandledNodeError
from abc import ABC, abstractmethod
from pydantic_core import ValidationError, core_schema
from typing_extensions import get_args
from pydantic import BaseModel, GetCoreSchemaHandler, ValidationInfo, TypeAdapter
from pydantic.fields import FieldInfo
from typing import Generic, TypeVar, Any, Literal
from inspect import signature

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
    """
    todo:
      - validate options class
    """

    __group__: str = None
    __sub_group__: str = None
    __label__: str = None
    __version__: int = 0

    def __repr__(self) -> str:
        return self.id()

    def __init__(
        self,
        input: BaseModel | dict | None = None,
        options: BaseModel | dict | None = None,
    ) -> None:
        # Check TypeAdapter(None).core_schema['type'] == 'none' to handle None case
        self._InputType = TypeAdapter(self.run.__annotations__.get("input"))
        self._OptionsType = TypeAdapter(self._get_options_model())
        input = self._coerce_defaults(input, self._InputType)
        options = self._coerce_defaults(options, self._OptionsType)
        self._input = self._InputType.validate_python(input)
        self._options = self._OptionsType.validate_python(options)
        self._run_params = {"input": self._input, "options": self._options}

    @classmethod
    def _get_options_model(cls) -> BaseModel | None:
        if hasattr(cls, "Options"):
            return cls.Options
        return None

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

    def call(self) -> run.__annotations__.get("return"):
        """This method is called by the system and should not be overridden.
        It inspects the signature of the run method and passes the correct
        arguments to it."""
        sig = signature(self.run)
        params = {k: v for k, v in self._run_params.items() if k in sig.parameters}
        OutputType = TypeAdapter(self.run.__annotations__.get("return"))

        try:
            ret = self.run(**params)
        except Exception as e:
            return self.error_handler(e)

        return OutputType.validate_python(ret)

    def error_handler(self, exception: Exception):
        """This method is called when an exception is raised in a node. It is
        passed the exception that was raised and should return a dict that
        will be returned to the user as the result of the node."""
        raise UnhandledNodeError(
            f"Unhandled exception in node {self._label}: {exception}"
        ) from exception

    @classmethod
    def schema(cls) -> NodeSchema:
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
            input=TypeAdapter(input_schema).json_schema(),
            output=TypeAdapter(output_schema).json_schema(),
            options=TypeAdapter(options_schema).json_schema(),
        )

    @staticmethod
    def _coerce_defaults(val: T, adapter: TypeAdapter) -> dict | None | T:
        if not val:
            if adapter.core_schema["type"] in ["none", "null"]:
                return None
            else:
                return {}
        return val


class NodeData:
    def __init__(self, model: BaseModel, type: Literal["input", "output"]) -> None:
        self.model = model
        self.type = type


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
