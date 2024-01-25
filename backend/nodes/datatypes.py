from pydantic import BaseModel


PrimitiveType = str | int | float | bool


class UndefinedMap(BaseModel):
    """
    An object type with an undefined schema
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert not self.model_fields, "UndefinedObject cannot have fields"


class Object(BaseModel):
    """
    An object type with a strict schema
    """

    pass
