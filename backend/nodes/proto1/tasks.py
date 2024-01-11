from nodes.base import Data, Task, Options
from pydantic import Field
from typing import Literal
from enum import Enum


class Selector(Task):
    """
    TODO: support arrays
    """
    def handler(self, data: Data, options: Options):
        return data[options.selected]

    def options(self, data_class: type[Data]):
        Selected = Enum("Selected", list(data_class.model_fields.keys()))

        class SelectorOptions(Options):
            selected: Selected

        return SelectorOptions
