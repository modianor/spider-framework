import time
from threading import Thread
from typing import List, Tuple

import requests

from config import Client
from core import logger
from core.task import Task
from handler import BaseHandler
from utils.single import Singleton
from utils.spiderqueue import ResultQueue


# logger = Logger(__name__).getlog()


@Singleton
class ResultProcess(object):

    def __init__(self) -> None:
        super().__init__()

    def processTaskResult(self, task: Task, result: Tuple):
        # taskType为List，任务结果目前为子任务参数，未来会扩展List任务返回值
        # taskType为Detail时，任务结果为实际下载数据，需要考虑上传失败和超时问题
        if task.taskType == 'List':
            data = {
                'task': str(task),
                'result': str(result[1])
            }
            requests.post(url='http://127.0.0.1:6048/task/uploadTaskParams', data=data)
        elif task.taskType == 'Data':
            pass
        elif task.taskType == 'Detail':
            pass
        else:
            # 任务类型错误
            pass


class ResultThread(Thread):

    def __init__(self, resultProcess: ResultProcess, resultQueue: ResultQueue, threadName: str, **kwds):
        Thread.__init__(self, **kwds)
        self.resultProcess = resultProcess
        self.resultQueue = resultQueue
        self.threadName = threadName
        self.parentThread = None
        self.close = False
        self.childThreadNum = Client.RESULT_HANDLER_NUM
        self.childThreads: List[ResultThread] = list()

    def __checkChildThreads__(self):
        if 'ResultHandler' == self.threadName:
            if len(self.childThreads) < self.childThreadNum:
                # 需要添加线程
                deltaThreadNum = self.childThreadNum - len(self.childThreads)
                for i in range(deltaThreadNum):
                    childThread = ResultThread(self.resultProcess,
                                               self.resultQueue,
                                               f'{self.threadName}_ChildThread_{i + 1}'
                                               )
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
                    self.resultProcess.processTaskResult(task, result)
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
        self.policyHandler: List[ResultThread] = list()
        self.resultQueue = resultQueue
        self.resultProcess = ResultProcess()
        self.resultProcessThread = None
        self.createHandlerProcess()

    def createHandlerProcess(self):
        self.resultProcessThread = ResultThread(resultProcess=self.resultProcess,
                                                resultQueue=self.resultQueue,
                                                threadName='ResultHandler'
                                                )
        self.resultProcessThread.start()

    def handle(self, result):
        pass
