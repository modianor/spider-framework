import time
import traceback
from threading import Thread
from typing import Dict

from framework.config import Client, Plugins
from framework.core import logger, status
from framework.core.lock import SpiderLock
from framework.core.policy import Policy
from framework.core.taskloader import TaskLoader
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
        # 爬虫进程任务加载器
        self.taskLoader = TaskLoader()

    def getTask(self):
        self.logger.info('GetTask Thread start')
        while True:
            try:
                if status.run:
                    try:
                        self.spiderLock.getTaskLock().acquire()
                        self.taskLoader.updatePolicies(self.policys)
                        self.taskLoader.supplyPolicyTasks()
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
            self.resultHandler = ResultHandler()
            self.taskHandler = TaskHandler(policyFetchers=self.policyFetchers)
        except:
            self.logger.error(f'Schedule初始化TaskHandle和ResultHandle失败, 错误原因:{traceback.format_exc()}')

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
