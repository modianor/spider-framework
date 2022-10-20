import time
import traceback
from threading import Thread
from typing import List, Tuple

from framework.config import Client
from framework.core import logger
from framework.core.task import Task
from framework.handler import BaseHandler
from framework.utils.single import Singleton
from framework.utils.spiderqueue import ResultQueue
# logger = Logger(__name__).getlog()
from framework.utils.taskpro import uploadTask


@Singleton
class ResultProcess(object):

    def __init__(self) -> None:
        super().__init__()

    def processTaskResult(self, task: Task, result: Tuple):
        # taskType为List，任务结果目前为子任务参数，未来会扩展List任务返回值
        # taskType为Detail时，任务结果为实际下载数据，需要考虑上传失败和超时问题
        if task.taskType == 'List':
            uploadTask(task, result)
        elif task.taskType == 'Data':
            uploadTask(task, result)
        elif task.taskType == 'Detail':
            uploadTask(task, result)
        else:
            # 任务类型错误
            pass


class ResultThread(Thread):

    def __init__(self, resultProcess: ResultProcess, threadName: str, **kwds):
        Thread.__init__(self, **kwds)
        self.resultProcess = resultProcess
        self.resultQueue = ResultQueue()
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
                                               # self.resultQueue,
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
            try:
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
            except:
                logger.error(f'{self.threadName}处理任务结果失败, 错误原因:\n{traceback.format_exc()}')

    def modifyClose(self):
        self.close = True


@Singleton
class ResultHandler(BaseHandler):
    def __init__(self) -> None:
        self.policyHandler: List[ResultThread] = list()
        self.resultQueue = ResultQueue()
        self.resultProcess = ResultProcess()
        self.resultProcessThread = None
        self.createHandlerProcess()

    def createHandlerProcess(self):
        self.resultProcessThread = ResultThread(resultProcess=self.resultProcess,
                                                # resultQueue=self.resultQueue,
                                                threadName='ResultHandler'
                                                )
        self.resultProcessThread.start()
