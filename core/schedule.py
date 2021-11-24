import logging
import time
from threading import Thread
from typing import Dict

from core.taskhandler import TaskHandler
from utils.cls_loader import load_object
from utils.config import PluginConfig
from utils.single import Singleton
from utils.spiderqueue import TaskQueue, ResultQueue
from utils.taskpro import randomTask


@Singleton
class Scheduler(object):
    def __init__(self) -> None:
        self.run = True
        self.taskQueue = TaskQueue()
        self.resultQueue = ResultQueue()
        self.fetchers = dict()
        self.loadFetchers()
        self.taskHandler = None
        self.logger = logging.getLogger('spider.scheduler')

    def getTask(self):
        self.logger.info('GetTask Thread start')
        while True:
            if self.run:
                if self.taskQueue.size() <= 10:
                    task = randomTask()
                    self.taskQueue.put(task)
                    # time.sleep(.5)
                else:
                    # self.logger.warning('task queue is full, wait 30 seconds...')
                    time.sleep(.5)

    def handleTask(self):
        self.logger.info('HandleTask Thread start')
        self.taskHandler = TaskHandler()
        while True:
            if not self.taskQueue.isEmpty():
                task = self.taskQueue.get()
                self.tryHandleTask(task)
            else:
                time.sleep(1)

    def tryHandleTask(self, task):
        while True:
            flag = self.taskHandler.handle(task)
            if flag:
                break
            else:
                time.sleep(1)

    def loadFetchers(self):
        config = PluginConfig()
        plugins: Dict = config.plugins
        for policyId in plugins:
            module = plugins[policyId]
            self.fetchers[policyId] = load_object(module)()

    def initSchedule(self):
        t1 = Thread(target=self.getTask, args=())
        t2 = Thread(target=self.handleTask, args=())
        threads = [t1, t2]

        for t in threads:
            t.setDaemon(False)
            t.start()
            time.sleep(0.5)

        for t in threads:
            t.join()
