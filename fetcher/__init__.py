import abc

from core.policy import Policy
from core.task import Task


class FetcherStatus:
    FAIL = 5
    SUCCESS = 4
    None_State = 6


class Fetcher(object, metaclass=abc.ABCMeta):

    def __init__(self) -> None:
        super().__init__()
        self.policy: Policy = None

    def setPolicy(self, policy: Policy):
        self.policy = policy

    @abc.abstractmethod
    def getList(self, task: Task):
        return

    @abc.abstractmethod
    def getDetail(self, task: Task):
        return

    @abc.abstractmethod
    def getData(self, task: Task):
        return
