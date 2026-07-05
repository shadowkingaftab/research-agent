from abc import ABC, abstractmethod


class Tool(ABC):

    name = ""

    @abstractmethod
    def run(self, task):
        pass