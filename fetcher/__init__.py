import abc


class FetcherStatus:
    FAIL = 5
    SUCCESS = 4
    None_State = 6


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
