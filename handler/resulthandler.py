import logging
import time
from threading import Thread
from typing import List

from config import Client
from handler import BaseHandler
from utils.log import Logger
from utils.single import Singleton
from utils.spiderqueue import ResultQueue

logger = Logger(__name__).getlog()


class ResultProcessThread(Thread):

    def __init__(self, resultQueue: ResultQueue, threadName: str, **kwds):
        Thread.__init__(self, **kwds)
        self.resultQueue = resultQueue
        self.threadName = threadName
        self.parentThread = None
        self.close = False
        self.childThreadNum = Client.RESULT_HANDLER_NUM
        self.childThreads: List[ResultProcessThread] = list()

    def __checkChildThreads__(self):
        if 'ResultHandler' == self.threadName:
            if len(self.childThreads) < self.childThreadNum:
                # 需要添加线程
                deltaThreadNum = self.childThreadNum - len(self.childThreads)
                for i in range(deltaThreadNum):
                    childThread = ResultProcessThread(self.resultQueue, f'{self.threadName}_ChildThread_{i + 1}')
                    self.childThreads.append(childThread)
                for childThread in self.childThreads:
                    childThread.start()
            else:
                # 需要删除线程
                deltaThreadNum = len(self.childThreads) - self.childThreadNum
                for i in range(deltaThreadNum):
                    childThread = self.childThreads[len(self.childThreads) - 1]
                    self.childThreads.remove(childThread)
                    childThread.modifyClose()

    def run(self) -> None:
        while True:
            if not self.close:
                self.__checkChildThreads__()
                if not self.resultQueue.isEmpty():
                    task, result = self.resultQueue.getResult()
                    logger.info(f'{self.threadName} handler a result: {result}')
                else:
                    # self.logger.info(f'{self.threadName} wait 1 second, because the result queue is empty')
                    time.sleep(0.1)
            else:
                logger.warning(f'{self.threadName} release')
                break

    def modifyClose(self):
        self.close = True


@Singleton
class ResultHandler(BaseHandler):
    def __init__(self, resultQueue: ResultQueue) -> None:
        self.logger = logging.getLogger('spider.ResultHandler')
        self.policyHandler: List[ResultProcessThread] = list()
        self.resultQueue = resultQueue
        self.resultProcessThread = None
        self.createHandlerProcess()
        # self.logger.info('ResultHandler start')

    def createHandlerProcess(self):
        self.resultProcessThread = ResultProcessThread(resultQueue=self.resultQueue, threadName='ResultHandler')
        self.resultProcessThread.start()

    def handle(self, result):
        pass
