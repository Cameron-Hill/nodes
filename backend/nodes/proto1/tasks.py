from nodes.base import Data, Task, Options
from pydantic import Field
from typing import Literal
from enum import Enum


class Selector(Task):
    def handler(self, data: Data, options: Options):
        return super().handler(data)

    def options(self, data_class: type[Data]):
        Selected = Enum("Selected", list(data_class.__fields__.keys()))

        class SelectorOptions(Options):
            selected: Selected

        return SelectorOptions
