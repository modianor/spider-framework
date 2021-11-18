import abc
import logging



class Fetcher(object, metaclass=abc.ABCMeta):

    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def getList(self, task):
        return

    @abc.abstractmethod
    def getDetail(self, task):
        return

    @abc.abstractmethod
    def getData(self, task):
        return
