from nodes.errors import UnhandledNodeError
from abc import ABC, abstractmethod
from pydantic_core import ValidationError, core_schema
from typing_extensions import get_args
from pydantic import BaseModel, GetCoreSchemaHandler, ValidationInfo, TypeAdapter
from pydantic.fields import FieldInfo
from typing import Generic, Type, TypeVar, Any, Literal
from inspect import signature, _empty

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


class NodeData:
    def __init__(
        self,
        parent: "Node",
        key: str,
        model: BaseModel,
        type: Literal["input", "output", "options"],
    ) -> None:
        self.key = key
        self.model = None if model is _empty else model
        self.type = type
        self.adapter: TypeAdapter = TypeAdapter(self.model)
        self._value = None
        self._set: bool = False
        self.parent = parent

    def set(self, value):
        self._value = self.adapter.validate_python(
            self._coerce_defaults(value, self.adapter)
        )
        self._set = True

    @property
    def value(self):
        assert self.is_set, "Value not set"
        return self._value

    @property  # type: ignore   I don't know why type checker was complaining
    def is_set(self) -> bool:
        return self._set

    @staticmethod
    def _coerce_defaults(val: T, adapter: TypeAdapter) -> dict | None | T:
        if not val:
            if adapter.core_schema["type"] in ["none", "null"]:
                return None
            else:
                return {}
        return val


class Node(ABC):
    """
    todo:
      - validate options class
    """

    __group__: str | None = None
    __sub_group__: str | None = None
    __label__: str | None = None
    __version__: int = 0

    def __repr__(self) -> str:
        return self.id()

    def __init__(self) -> None:
        self.options: dict[str, NodeData] = self._get_options()
        self.inputs: dict[str, NodeData] = self._get_inputs(self.options)
        self.data: dict[str, NodeData] = {**self.inputs, **self.options}
        self.output: NodeData = self._get_output()

    def _get_options(self) -> dict[str, NodeData]:
        if not hasattr(self, "Options"):
            return {}
        sig = signature(self.run)
        options = {}
        Options = getattr(self, "Options")
        for i, (key, param) in enumerate(sig.parameters.items()):
            if i and param.annotation == Options:
                options[key] = NodeData(self, key, Options, type="options")
        return options

    def _get_inputs(self, options: dict[str, NodeData]) -> dict[str, NodeData]:
        sig = signature(self.run)
        inputs = {}
        for key, param in sig.parameters.items():
            if (
                param is not self and key not in options
            ):  # always ignore for param because it is an instance method
                inputs[key] = NodeData(self, key, param.annotation, type="input")
        return inputs

    def _get_output(self) -> NodeData:
        sig = signature(self.run)
        return NodeData(self, "output", sig.return_annotation, type="output")

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

    def call(self, **inputs) -> run.__annotations__.get("return"):
        """This method is called by the system and should not be overridden.
        It inspects the signature of the run method and passes the correct
        arguments to it."""
        for key, data_node in self.data.items():
            data_node.set(inputs.get(key))
        params = {k: v.value for k, v in self.data.items()}

        try:
            ret = self.run(**params)
        except Exception as e:
            return self.error_handler(e)

        return self.output.adapter.validate_python(ret)

    def error_handler(self, exception: Exception):
        """This method is called when an exception is raised in a node. It is
        passed the exception that was raised and should return a dict that
        will be returned to the user as the result of the node."""
        raise UnhandledNodeError(
            f"Unhandled exception in node {self.label()}: {exception}"
        ) from exception

    @classmethod
    def schema(cls) -> NodeSchema:
        """Return the schema for the node."""
        input_schema = cls.run.__annotations__.get("input")
        output_schema = cls.run.__annotations__.get("return")
        options_schema = getattr(cls, "Options") if hasattr(cls, "Options") else None

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
