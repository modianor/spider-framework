import time
import traceback
from threading import Thread
from typing import Dict
from urllib.parse import urljoin

import requests

from config import Client, Plugins
from core import logger
from core.policy import Policy
from core.task import Task
from fetcher import Fetcher
from handler.resulthandler import ResultHandler
from handler.taskhandler import TaskHandler
from utils.cls_loader import load_object
from utils.single import Singleton
from utils.spiderqueue import TaskQueue, ResultQueue


@Singleton
class Scheduler(object):
    def __init__(self) -> None:
        self.logger = logger
        self.run = True
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

    def getTask(self):
        self.logger.info('GetTask Thread start')
        while True:
            try:
                if self.run:
                    if self.taskQueue.size() <= Client.TASK_QUEUE_SIZE:
                        data = {'policyIds': ['HEIMAOTOUSU']}
                        url = urljoin(Client.BASE_URL, './getTaskParams')
                        response = requests.post(url=url, data=data)
                        task_params = response.json()
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
                else:
                    self.logger.info('spider is pause, waiting to wake up')
                    time.sleep(Client.Fetch_Wait_Interval)
            except:
                self.logger.error(f'Schedule获取任务错误, 错误原因:{traceback.format_exc()}')
                time.sleep(Client.Fetch_Wait_Interval * 5)

    def handleTask(self):
        try:
            self.logger.info('HandleTask Thread start')
            self.taskHandler = TaskHandler(policyFetchers=self.policyFetchers, resultQueue=self.resultQueue)
            self.resultHandler = ResultHandler(resultQueue=self.resultQueue)
        except:
            self.logger.error(f'Schedule初始化TaskHandle和ResultHandle失败, 错误原因:{traceback.format_exc()}')

        while True:
            try:
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

    def loadFetchers(self):
        plugins: Dict = Plugins.plugins
        for policyId in plugins:
            module = plugins[policyId]
            fetcher = load_object(module)()
            self.policyFetchers[policyId] = fetcher
            self.logger.info(f'load {module} successfully')

    def getPolicyInfos(self):
        # 更新所有启动策略的基本信息
        policy = Policy(policyId='HEIMAOTOUSU',
                        proxy=0,
                        interval=0,
                        duplicate=None,
                        taskQueueSize=4,
                        timeout=60,
                        retryTimes=3)
        fetcher = self.policyFetchers[policy.policyId]
        # 模拟更新爬取策略
        fetcher.setPolicy(policy)

    def getHostInfo(self):
        # 更新进程主机运行参数和策略对应处理的任务
        pass

    def initSchedule(self):
        t1 = Thread(target=self.getPolicyInfos, args=())
        t2 = Thread(target=self.getHostInfo, args=())
        t3 = Thread(target=self.getTask, args=())
        t4 = Thread(target=self.handleTask, args=())
        threads = [t1, t2, t3, t4]

        for t in threads:
            t.setDaemon(False)
            t.start()
            time.sleep(0.5)
