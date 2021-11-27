import time
from threading import Thread

import requests

from config import Client
from core import logger
from core.task import Task
from handler.resulthandler import ResultHandler
from handler.taskhandler import TaskHandler
from utils.single import Singleton
from utils.spiderqueue import TaskQueue, ResultQueue


@Singleton
class Scheduler(object):
    def __init__(self) -> None:
        self.run = True
        self.taskQueue = TaskQueue()
        self.resultQueue = ResultQueue()
        self.taskHandler = None
        self.resultHandler = None

        self.logger = logger

    def getTask(self):
        self.logger.info('GetTask Thread start')
        while True:
            if self.run:
                if self.taskQueue.size() <= Client.TASKQUEUE_SZIE:
                    data = {
                        'policyIds': ['HEIMAOTOUSU']
                    }
                    response = requests.post(url='http://127.0.0.1:6048/task/getTaskParams', data=data)
                    task_params = response.json()
                    for task_param in task_params:
                        try:
                            task = Task.fromJson(**task_param)
                            self.taskQueue.put(task)
                        except TypeError:
                            pass
                            # self.logger.warning('任务为空，爬虫进程继续等待任务')
                    time.sleep(Client.Fetch_Interval)
                else:
                    time.sleep(Client.Fetch_Wait_Interval)
            else:
                time.sleep(Client.Fetch_Wait_Interval)

    def handleTask(self):
        self.logger.info('HandleTask Thread start')
        self.taskHandler = TaskHandler(resultQueue=self.resultQueue)
        self.resultHandler = ResultHandler(resultQueue=self.resultQueue)
        while True:
            if not self.taskQueue.isEmpty():
                # 任务队列不为空，尝试处理任务
                task = self.taskQueue.get()
                self.tryHandleTask(task)
            else:
                # 任务队列为空，等待新的任务进入任务队列
                time.sleep(Client.Handle_Task_Wait_Interval)

    def tryHandleTask(self, task):
        while True:
            flag = self.taskHandler.handle(task)
            if flag:
                break
            else:
                time.sleep(Client.Handle_Task_Interval)

    def initSchedule(self):
        t1 = Thread(target=self.handleTask, args=())
        t2 = Thread(target=self.getTask, args=())
        threads = [t1, t2]

        for t in threads:
            t.setDaemon(False)
            t.start()
            time.sleep(0.5)

        # for t in threads:
        #     t.join()
