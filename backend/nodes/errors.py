class NodeError(Exception):
    """Base class for all exceptions in this module."""

    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)


class UnhandledNodeError(NodeError):
    """Raised when an exception is raised in a node and is not handled by the
    node's error handler."""

    pass


class NodeDataException(Exception):
    """"""


class NodeDataSchemaValidationException(NodeDataException):
    """
    Raised when a node data is not valid.
    """


class NodeDataNotSetException(NodeDataException):
    """
    Raised when a node data is not set.
    """
