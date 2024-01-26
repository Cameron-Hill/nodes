from pydantic import BaseModel

PrimitiveType = str | int | float | bool


class UndefinedMap(BaseModel):
    """
    An object type with an undefined schema
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert not self.model_fields, "UndefinedObject cannot have fields"


class Undefined:
    """Implies the annotated type is undefined or partially defined and may need
    strict coercion to be consumed by downstream models"""


class Object(BaseModel):
    """
    An object type with a strict schema
    """

    pass
