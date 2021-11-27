import time
import traceback
from threading import Thread
from typing import Dict, List

from config import Plugins
from core import logger
from core.task import Task
from fetcher import Fetcher
from handler import BaseHandler
from utils.cls_loader import load_object
from utils.single import Singleton
from utils.spiderqueue import TaskQueue, ResultQueue


class FetcherThread(Thread):

    def __init__(self, policyId, fetcherInstance: Fetcher, policyTaskQueue: TaskQueue, resultQueue: ResultQueue,
                 threadName: str, **kwds):
        Thread.__init__(self, **kwds)
        self.policyId = policyId
        self.close = False
        self.fetcherInstance = fetcherInstance
        self.policyTaskQueue = policyTaskQueue
        self.resultQueue = resultQueue
        self.threadName = threadName
        self.parentThread = None
        self.childThreadNum = 0
        self.childThreads: List[FetcherThread] = list()
        logger.info(f'{self.threadName} start')

    def __checkChildThreads__(self):
        if 'ParentThread' in self.threadName:
            if len(self.childThreads) == self.childThreadNum:
                pass
            elif len(self.childThreads) < self.childThreadNum:
                # 需要添加子线程
                deltaThreadNum = self.childThreadNum - len(self.childThreads)
                for i in range(deltaThreadNum):
                    childThread = FetcherThread(policyId=self.policyId,
                                                fetcherInstance=self.fetcherInstance,
                                                policyTaskQueue=self.policyTaskQueue,
                                                resultQueue=self.resultQueue,
                                                threadName=f'{self.policyId}_ChildThread_{i + 1}')
                    self.childThreads.append(childThread)
                for childThread in self.childThreads:
                    childThread.start()
            else:
                # 需要删除子线程
                deltaThreadNum = len(self.childThreads) - self.childThreadNum
                for i in range(deltaThreadNum):
                    childThread = self.childThreads[len(self.childThreads) - 1]
                    self.childThreads.remove(childThread)
                    childThread.modifyClose()

    def run(self) -> None:
        while True:
            if not self.close:
                self.__checkChildThreads__()
                if not self.policyTaskQueue.isEmpty():
                    # logger.info(f'{self.threadName} handler a task')
                    try:
                        task = self.policyTaskQueue.getTask()
                        result = None
                        taskType = task.taskType
                        if taskType == 'List':
                            # (taskStatus,[[urlSign, companyName, creditCode,#{policyId}:{taskType}#]],kibanalog)
                            result = self.fetcherInstance.getList(task)
                        elif taskType == 'Detail':
                            # (taskStatus,{k1:v1, k2:v2, k3:v3}],kibanalog)
                            result = self.fetcherInstance.getDetail(task)
                        elif taskType == 'Data':
                            # (taskStatus,{k1:v1, k2:v2, k3:v3}],kibanalog)
                            result = self.fetcherInstance.getData(task)
                        self.resultQueue.putResult((task, result))
                    except:
                        logger.error(traceback.format_exc())
                else:
                    time.sleep(1)
            else:
                logger.warning(f'{self.threadName} release')
                break

    def modifyClose(self):
        self.close = True


@Singleton
class TaskHandler(BaseHandler):
    def __init__(self, resultQueue: ResultQueue) -> None:
        # 业务策略Handler
        self.policyHandler: Dict[str, FetcherThread] = dict()
        # 业务策略任务队列
        self.policyTaskQueues: Dict[str, TaskQueue] = dict()
        # 业务策略Fetcher
        self.policyFetchers: Dict[str, Fetcher] = dict()
        # 业务策略结果队列
        self.resultQueue = resultQueue
        # 加载业务策略Fetcher
        self.loadFetchers()
        self.createHandlerProcess()

    def loadFetchers(self):
        plugins: Dict = Plugins.plugins
        for policyId in plugins:
            module = plugins[policyId]
            fetcher = load_object(module)()
            self.policyFetchers[policyId] = fetcher
            logger.info(f'load {module} successfully')

        for policyId in self.policyFetchers:
            taskQueue = TaskQueue()
            fetcher = self.policyFetchers[policyId]
            self.policyTaskQueues[policyId] = taskQueue
            self.policyHandler[policyId] = FetcherThread(policyId=policyId,
                                                         fetcherInstance=fetcher,
                                                         policyTaskQueue=taskQueue,
                                                         resultQueue=self.resultQueue,
                                                         threadName=f'{policyId}_ParentThread')

    def createHandlerProcess(self):
        for policyId in self.policyHandler:
            policyIdThread = self.policyHandler[policyId]
            policyIdThread.start()

    def handle(self, task: Task):
        policyId = task.policyId
        policyTaskQueue = self.policyTaskQueues[policyId]
        if policyTaskQueue.size() < 2:
            self.policyTaskQueues[policyId].putTask(task)
            return True
        else:
            # self.logger.warning(f'policyId:{policyId} policyTaskQueue is full')
            return False
