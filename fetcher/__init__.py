import abc

from core.policy import Policy
from core.task import Task


class FetcherStatus:
    SUCCESS = 4
    FAIL = 5
    None_State = 6


class Fetcher(object, metaclass=abc.ABCMeta):

    def __init__(self) -> None:
        super().__init__()
        self.policy: Policy = None
        self.myRequest = None

    def setPolicy(self, policy: Policy):
        self.policy = policy

    def getContent(self, url, params=None, data=None, headers=None, method='GET'):
        res, resp = self.myRequest.getContent(url=url,
                                              method=method,
                                              params=params,
                                              headers=headers,
                                              data=data,
                                              timeout=self.policy.timeout,
                                              retryTimes=self.policy.retryTimes,
                                              interval=self.policy.interval,
                                              proxy=self.policy.proxy)

        return res, resp

    @abc.abstractmethod
    def getList(self, task: Task):
        return

    @abc.abstractmethod
    def getDetail(self, task: Task):
        return

    @abc.abstractmethod
    def getData(self, task: Task):
        return
