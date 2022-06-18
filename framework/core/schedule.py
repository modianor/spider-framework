import time
import traceback
from threading import Thread
from typing import Dict
from urllib.parse import urljoin

import requests

from framework.config import Client, Plugins
from framework.core import logger, status
from framework.core.lock import SpiderLock
from framework.core.policy import Policy
from framework.core.task import Task
from framework.fetcher import Fetcher
from framework.handler.resulthandler import ResultHandler
from framework.handler.taskhandler import TaskHandler
from framework.utils.cls_loader import load_object
from framework.utils.params import getPolicy
from framework.utils.single import Singleton
from framework.utils.spiderqueue import TaskQueue, ResultQueue


@Singleton
class Scheduler(object):
    def __init__(self) -> None:
        self.logger = logger
        # 爬虫进程加载的插件对应策略
        self.policys: Dict[str, Policy or None] = dict()
        # 爬虫进程任务队列
        self.taskQueue = TaskQueue()
        # 爬虫进程结果队列
        self.resultQueue = ResultQueue()
        # 爬虫进程任务处理器
        self.taskHandler = None
        # 爬虫任务结果处理器
        self.resultHandler = None
        # 爬虫进程需要加载的策略和对应插件
        self.policyFetchers: Dict[str, Fetcher] = dict()
        # 主动加载
        self.loadFetchers()
        # 爬虫进程持有锁的对象
        self.spiderLock = SpiderLock()

    def getTask(self):
        self.logger.info('GetTask Thread start')
        while True:
            try:
                if status.run:
                    try:
                        self.spiderLock.getTaskLock().acquire()
                        if self.taskQueue.size() <= Client.TASK_QUEUE_SIZE:
                            policyIds = list()
                            for policyId in self.policys:
                                policy = self.policys[policyId]
                                if policy is None:
                                    continue
                                if policy.taskTypesInfo is None or policy.taskTypesInfo == '':
                                    continue
                                taskParams = f'{policy.policyId}:{"|".join(policy.taskTypes)}'
                                policyIds.append(taskParams)
                            if len(policyIds) == 0:
                                continue
                            logger.info(f'正在尝试获取任务:{";".join(policyIds)}')
                            data = {'policyIds': policyIds, 'processName': Client.PROCESS_NAME}
                            url = urljoin(Client.BASE_URL, './getTaskParams')
                            response = requests.post(url=url, data=data)
                            task_params = response.json()

                            if len(task_params) == 0:
                                time.sleep(Client.Fetch_Interval * 5)

                            for task_param in task_params:
                                try:
                                    task = Task.fromJson(**task_param)
                                    self.taskQueue.putTask(task)
                                except TypeError:
                                    pass
                                    # self.logger.warning('任务为空，爬虫进程继续等待任务')
                            time.sleep(Client.Fetch_Interval)
                        else:
                            time.sleep(Client.Fetch_Wait_Interval)
                    except:
                        pass
                    finally:
                        self.spiderLock.getTaskLock().release()
                else:
                    self.logger.info('spider is pause, waiting to wake up')
                    time.sleep(Client.Fetch_Wait_Interval * 5)
            except:
                self.logger.error(f'Schedule获取任务错误, 错误原因:{traceback.format_exc()}')
                time.sleep(Client.Fetch_Wait_Interval)

    def handleTask(self):
        try:
            self.logger.info('HandleTask Thread start')
            self.taskHandler = TaskHandler(policyFetchers=self.policyFetchers, resultQueue=self.resultQueue)
            self.resultHandler = ResultHandler(resultQueue=self.resultQueue)
        except:
            self.logger.error(f'Schedule初始化TaskHandle和ResultHandle失败, 错误原因:{traceback.format_exc()}')

        while True:
            try:
                self.spiderLock.getTaskLock().acquire()
                if not self.taskQueue.isEmpty():
                    # 任务队列不为空，尝试处理任务
                    task = self.taskQueue.getTask()
                    handleStatus = self.taskHandler.handle(task)
                    if not handleStatus:
                        self.taskQueue.putTask(task)
                else:
                    # 任务队列为空，等待新的任务进入任务队列
                    time.sleep(Client.Handle_Task_Wait_Interval)
            except:
                self.logger.error(f'Schedule处理任务错误, 错误原因:{traceback.format_exc()}')
                time.sleep(Client.Handle_Task_Wait_Interval * 5)
            finally:
                self.spiderLock.getTaskLock().release()

    def loadFetchers(self):
        plugins: Dict = Plugins.plugins
        for policyId in plugins:
            module = plugins[policyId]
            fetcher = load_object(module)()
            self.policys[policyId] = None
            self.policyFetchers[policyId] = fetcher
            self.logger.info(f'load {module} successfully')

    def getPolicyInfos(self):
        # 更新所有启动策略的基本信息
        while True:
            policys = getPolicy(list(self.policys.keys()))
            for policy in policys:
                self.logger.info(f'update policy {policy}')
                self.updatePolicy(policy=policy)

            # 每隔10分钟更新1次插件对应策略
            time.sleep(60 * 10)

    def updatePolicy(self, policy: Policy):
        # 更新爬取策略
        policyId = policy.policyId
        self.policys[policyId] = policy
        fetcher = self.policyFetchers[policyId]
        fetcher.setPolicy(policy)

    def initSchedule(self):
        t1 = Thread(target=self.getPolicyInfos, args=())
        # t2 = Thread(target=self.getHostInfo, args=())
        t3 = Thread(target=self.getTask, args=())
        t4 = Thread(target=self.handleTask, args=())
        # threads = [t1, t2, t3, t4]
        threads = [t1, t3, t4]

        for t in threads:
            t.setDaemon(False)
            t.start()
            time.sleep(0.5)
