from nodes.errors import UnhandledNodeError
from abc import ABC, abstractmethod
from pydantic_core import ValidationError, core_schema
from typing_extensions import get_args
from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    ValidationInfo,
    TypeAdapter,
    ValidationError,
)
from pydantic.fields import FieldInfo
from typing import Generic, Type, TypeVar, Any, Literal
from inspect import signature, _empty, Parameter
from dataclasses import dataclass
from shortuuid import uuid
from logging import getLogger
import json

logger = getLogger(__name__)

T = TypeVar("T")
UNSET = object()


class Option(BaseModel):
    """Options are like inputs that are provided to the node ahead of execution.
    Options must be object-type base models that are a subclass of this option class.
    """


class NodeSchema(BaseModel):
    """This class represents the schema for a node."""

    label: str
    address: str
    group: str | None
    sub_group: str | None
    version: int
    inputs: dict | None
    output: dict | None
    options: dict | None


NodeDataTypes = Literal["input", "output", "options"]


class NodeData:
    def __init__(
        self,
        node: "Node",
        key: str,
        model: BaseModel,
        type: NodeDataTypes,
        value=UNSET,
    ) -> None:
        self.key = key
        self.model = None if model is _empty else model
        self.type: NodeDataTypes = type
        self.adapter: TypeAdapter = TypeAdapter(self.model)
        self._value = value
        self._set: bool = False
        self.node = node
        if value is not UNSET:
            self._set = True
        self.set_default()

    def set_default(self):
        try:
            self.set(None)
        except ValidationError:
            logger.debug(f"Cannot set default for {self.type} Node Data {self.key}")

    def validate(self, value: Any) -> Any:
        try:
            return self.adapter.validate_python(
                self._coerce_defaults(value, self.adapter)
            )
        except ValidationError as e:
            msg = f"'{value}' is an invalid type for '{str(self.model)}'"
            details = {
                "msg": msg,
                "title": e.title,
                "schema": self.adapter.json_schema(),
            }

            e.add_note(json.dumps(details))
            raise e

    def set(self, value):
        self._value = self.validate(value)
        self._set = True

    @property
    def value(self) -> Any:
        assert self.is_set, "Value not set"
        return self._value

    @property  # type: ignore   I don't know why type checker was complaining
    def is_set(self) -> bool:
        return not self._value is UNSET

    @property
    def unset(self) -> bool:
        return self._value is UNSET

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
        return self.address()

    def __init__(self, id: str | None = None) -> None:
        self.id: str = id or uuid()
        self.options: dict[str, NodeData] = self._get_options()
        self.inputs: dict[str, NodeData] = self._get_inputs(self.options)
        self.data: dict[str, NodeData] = {**self.inputs, **self.options}
        self.output: NodeData = self._get_output()

    @property
    def options_set(self) -> bool:
        return all([data.is_set for data in self.options.values()])

    @property
    def ready(self) -> bool:
        """
        A node is ready if:
         - All data is set.
        """
        return all(data.is_set for data in self.data.values())

    @classmethod
    def _get_option_params(cls) -> dict[str, Parameter]:
        sig = signature(cls.run)
        OptionClass = getattr(cls, "Options", None)
        if not OptionClass:
            return {}
        params = {}
        for i, (key, param) in enumerate(sig.parameters.items()):
            if (
                not (i == 0 and param.name == "self")
                and param.annotation == OptionClass
            ):
                params[key] = param
        return params

    @classmethod
    def _get_input_params(cls) -> dict[str, Parameter]:
        sig = signature(cls.run)
        options = cls._get_option_params()
        inputs = {}
        for i, (key, param) in enumerate(sig.parameters.items()):
            if not (i == 0 and param.name == "self") and key not in options:
                inputs[key] = param
        return inputs

    def _get_options(self) -> dict[str, NodeData]:
        params = self._get_option_params()
        return {
            k: NodeData(self, k, v.annotation, type="options")
            for k, v in params.items()
        }

    def _get_inputs(self, options: dict[str, NodeData]) -> dict[str, NodeData]:
        params = self._get_input_params()
        return {
            k: NodeData(self, k, v.annotation, type="input")
            for k, v in params.items()
            if k not in options
        }

    def _get_output(self) -> NodeData:
        sig = signature(self.run)
        return NodeData(self, "output", sig.return_annotation, type="output")

    @classmethod
    def address(cls):
        return f"{cls.__module__}.{cls.__name__}"

    @classmethod
    def label(cls):
        return cls.__label__ or cls.__name__

    @abstractmethod
    def run(self, input: BaseModel | None, options: BaseModel | None):
        """This method is called when the node is run. It is passed the input
        data and should return a dict that will be passed to the next node."""
        raise NotImplementedError

    def call(self, **inputs) -> Any:  # run.__annotations__.get("return"):
        """This method is called by the system and should not be overridden.
        It inspects the signature of the run method and passes the correct
        arguments to it."""
        for key, value in inputs.items():
            if key in self.data:
                self.data[key].set(value)

        if unset := [k for k, v in self.data.items() if not v.is_set]:
            raise ValueError(
                f"Cannot Call Node: {self.label()} due to unset Inputs: {unset}"
            )

        params = {k: v.value for k, v in self.data.items()}

        try:
            ret = self.run(**params)
        except Exception as e:
            return self.error_handler(e)

        self.output.set(ret)

        return self.output.value

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
        output_schema = cls.run.__annotations__.get("return")
        input_params = cls._get_input_params()
        option_params = cls._get_option_params()
        input_schema = {
            k: TypeAdapter(v.annotation).json_schema() for k, v in input_params.items()
        }
        options_schema = {
            k: TypeAdapter(v.annotation).json_schema() for k, v in option_params.items()
        }

        return NodeSchema(
            address=cls.address(),
            label=cls.label(),
            group=cls.__group__,
            sub_group=cls.__sub_group__,
            version=cls.__version__,
            inputs=input_schema,
            output=TypeAdapter(output_schema).json_schema(),
            options=options_schema,
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


@dataclass(eq=True, frozen=True)
class Edge:
    source: NodeData
    target: NodeData
