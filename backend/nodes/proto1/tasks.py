from nodes.base import Data, Task, Options


class Selector(Task):
    def handler(self, data: Data, options: Options):
        return super().handler(data)
    
    def options(self, data_class: type[Data]):
        a=1