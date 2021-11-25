import time
from threading import Thread

from config import Client
from handler.resulthandler import ResultHandler
from handler.taskhandler import TaskHandler
from utils.log import Logger
from utils.single import Singleton
from utils.spiderqueue import TaskQueue, ResultQueue
from utils.taskpro import randomTask


@Singleton
class Scheduler(object):
    def __init__(self) -> None:
        self.run = True
        self.taskQueue = TaskQueue()
        self.resultQueue = ResultQueue()
        self.taskHandler = None
        self.resultHandler = None

        self.logger = Logger(__name__).getlog()

    def getTask(self):
        self.logger.info('GetTask Thread start')
        while True:
            if self.run:
                if self.taskQueue.size() <= Client.TASKQUEUE_SZIE:
                    task = randomTask()
                    self.taskQueue.put(task)
                    time.sleep(Client.Fetch_Interval)
                    break
                else:
                    # self.logger.warning('task queue is full, wait 30 seconds...')
                    time.sleep(1)

    def handleTask(self):
        self.taskHandler = TaskHandler(resultQueue=self.resultQueue)
        self.resultHandler = ResultHandler(resultQueue=self.resultQueue)
        while True:
            if not self.taskQueue.isEmpty():
                task = self.taskQueue.get()
                self.tryHandleTask(task)
                time.sleep(.5)
            else:
                time.sleep(1)

    def tryHandleTask(self, task):
        while True:
            flag = self.taskHandler.handle(task)
            if flag:
                break
            else:
                time.sleep(1)

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
