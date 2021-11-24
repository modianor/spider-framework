import logging
import time
from threading import Thread
from typing import Dict, List

from core.task import Task
from fetcher import Fetcher
from utils.cls_loader import load_object
from utils.config import PluginConfig
from utils.spiderqueue import TaskQueue


class FetcherThread(Thread):

    def __init__(self, policyId, fetcherInstance: Fetcher, policyTaskQueue: TaskQueue, threadName: str, **kwds):
        Thread.__init__(self, **kwds)
        self.logger = logging.getLogger('spider.TaskHandler.FetcherThread')
        self.policyId = policyId
        self.close = False
        self.fetcherInstance = fetcherInstance
        self.policyTaskQueue = policyTaskQueue
        self.threadName = threadName
        self.parentThread = None
        self.childThreadNum = 1
        self.childThreads: List[FetcherThread] = list()
        self.logger.info(f'{self.threadName} start')

    def __checkChildThreads__(self):
        if 'ParentThread' in self.threadName:
            if len(self.childThreads) < self.childThreadNum:
                # 需要添加子线程
                deltaThreadNum = self.childThreadNum - len(self.childThreads)
                for i in range(deltaThreadNum):
                    childThread = FetcherThread(self.policyId, self.fetcherInstance, self.policyTaskQueue,
                                                f'{self.policyId}_ChildThread_{i + 1}')
                    self.childThreads.append(childThread)
                for childThread in self.childThreads:
                    childThread.start()
                # self.childThreadNum = 0
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
                    self.logger.info(f'{self.threadName} handler a task')
                    task = self.policyTaskQueue.getTask()
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
                else:
                    pass
                    # self.logger.info(f'{self.threadName} wait 1 second...')
                    time.sleep(1)
            else:
                self.logger.warning(f'{self.threadName} release')
                break

    def modifyClose(self):
        self.close = True


class TaskHandler(object):
    def __init__(self) -> None:
        self.logger = logging.getLogger('spider.TaskHandler')
        self.policyHandler: Dict[str, FetcherThread] = dict()
        self.policyTaskQueues: Dict[str, TaskQueue] = dict()
        self.loadFetchers()

    def loadFetchers(self):
        config = PluginConfig()
        plugins: Dict = config.plugins
        for policyId in plugins:
            module = plugins[policyId]
            fetcher = load_object(module)()
            taskQueue = TaskQueue()
            self.policyTaskQueues[policyId] = taskQueue
            self.policyHandler[policyId] = FetcherThread(policyId=policyId, fetcherInstance=fetcher,
                                                         policyTaskQueue=taskQueue,
                                                         threadName=f'{policyId}_ParentThread')
        for policyId in self.policyHandler:
            policyIdThread = self.policyHandler[policyId]
            policyIdThread.start()

    def handle(self, task: Task):
        policyId = task.policyId
        policyTaskQueue = self.policyTaskQueues[policyId]
        if policyTaskQueue.size() < 10:
            self.policyTaskQueues[policyId].putTask(task)
            return True
        else:
            self.logger.warning(f'policyId:{policyId} policyTaskQueue is full')
            return False
