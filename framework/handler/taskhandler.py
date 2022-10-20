import time
import traceback
from threading import Thread
from typing import Dict, List

from framework.core import logger
from framework.core.taskloader import TaskLoader
from framework.fetcher import Fetcher
from framework.handler import BaseHandler
from framework.utils.single import Singleton
from framework.utils.spiderqueue import ResultQueue


class FetcherThread(Thread):

    def __init__(self, policyId, fetcherInstance: Fetcher, threadName: str, **kwds):
        Thread.__init__(self, **kwds)
        self.policyId = policyId
        self.close = False
        self.fetcherInstance = fetcherInstance
        # self.policyTaskQueue = policyTaskQueue
        self.resultQueue = ResultQueue()
        self.threadName = threadName
        self.parentThread = None
        self.childThreadNum = 0
        self.childThreads: List[FetcherThread] = list()
        # 爬虫进程任务加载器
        self.taskLoader = TaskLoader()
        logger.info(f'{self.threadName} start')

    def __checkChildThreads__(self):
        if 'ParentThread' in self.threadName:
            try:
                self.childThreadNum = self.fetcherInstance.policy.childThreadNum
            except:
                self.childThreadNum = 0
            if len(self.childThreads) == self.childThreadNum:
                pass
            elif len(self.childThreads) < self.childThreadNum:
                # 需要添加子线程
                deltaThreadNum = self.childThreadNum - len(self.childThreads)
                for i in range(len(self.childThreads), self.childThreadNum):
                    childThread = FetcherThread(policyId=self.policyId,
                                                fetcherInstance=self.fetcherInstance,
                                                # policyTaskQueue=self.policyTaskQueue,
                                                # resultQueue=self.resultQueue,
                                                threadName=f'{self.policyId}_ChildThread_{i + 1}')
                    self.childThreads.append(childThread)
                    childThread.start()
                    logger.warn(f'父线程{self.threadName}正在添加子线程{childThread.threadName}')
                logger.warn(f'{[childThread.threadName for childThread in self.childThreads]}')

            else:
                # 需要删除子线程
                deltaThreadNum = len(self.childThreads) - self.childThreadNum
                for i in range(deltaThreadNum):
                    childThread = self.childThreads[len(self.childThreads) - 1]
                    logger.warn(f'父线程{self.threadName}正在删除子线程{childThread.threadName}')
                    self.childThreads.remove(childThread)
                    childThread.modifyClose()
                logger.warn(f'{[childThread.threadName for childThread in self.childThreads]}')

    def run(self) -> None:
        while True:
            if not self.close:
                self.__checkChildThreads__()
                try:
                    # 这里任务可能是通用插件任务，也有可能是通用配置任务，个人觉得通用配置爬虫需要单独占用一个进程
                    task = self.taskLoader.getTaskByPolicyId(self.policyId)
                    if task is not None:
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
                    else:
                        time.sleep(1)
                except:
                    logger.error(traceback.format_exc())
            else:
                logger.warning(f'{self.threadName} release')
                break

    def modifyClose(self):
        self.close = True


@Singleton
class TaskHandler(BaseHandler):
    def __init__(self, policyFetchers: Dict[str, Fetcher]) -> None:
        # 业务策略Handler
        self.policyHandler: Dict[str, FetcherThread] = dict()
        # 业务策略任务队列
        # self.policyTaskQueues: Dict[str, TaskQueue] = dict()
        # 业务策略Fetcher
        self.policyFetchers: Dict[str, Fetcher] = policyFetchers
        # 业务策略结果队列
        # self.resultQueue = resultQueue
        # 创建业务Handle线程
        self.createHandlerProcess()

    def createHandlerProcess(self):
        for policyId in self.policyFetchers:
            # taskQueue = TaskQueue()
            fetcher = self.policyFetchers[policyId]
            # self.policyTaskQueues[policyId] = taskQueue
            self.policyHandler[policyId] = FetcherThread(policyId=policyId,
                                                         fetcherInstance=fetcher,
                                                         # policyTaskQueue=taskQueue,
                                                         # resultQueue=self.resultQueue,
                                                         threadName=f'{policyId}_ParentThread')

        for policyId in self.policyHandler:
            policyIdThread = self.policyHandler[policyId]
            policyIdThread.start()
