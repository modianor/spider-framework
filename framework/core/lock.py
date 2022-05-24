import threading

from framework.utils.single import Singleton


@Singleton
class SpiderLock(object):

    def __init__(self) -> None:
        super().__init__()
        self.taskLock: threading.Lock = threading.Lock()

    def getTaskLock(self) -> threading.Lock:
        return self.taskLock
