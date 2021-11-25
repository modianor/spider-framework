import time
from random import Random

from core.task import Task
from fetcher import Fetcher
from utils.log import Logger


class XueQiuFetcher(Fetcher):

    def __init__(self) -> None:
        super().__init__()
        self.policyId = 'XUEQIU'
        self.logger = Logger(__name__).getlog()

    def getList(self, task: Task):
        self.logger.info(f'{task.taskId}, {task.taskType}, {task.policyId}')
        t = Random().randint(1, 5)
        # self.logger.info(f'run getList method, take {t} seconds...')
        time.sleep(t)
        pass

    def getDetail(self, task: Task):
        self.logger.info(f'{task.taskId}, {task.taskType}, {task.policyId}')
        t = Random().randint(1, 5)
        # self.logger.info(f'run getDetail method, take {t} seconds...')
        time.sleep(t)
        pass

    def getData(self, task: Task):
        self.logger.info(f'{task.taskId}, {task.taskType}, {task.policyId}')
        t = Random().randint(1, 5)
        # self.logger.info(f'run getData method, take {t} seconds...')
        time.sleep(t)
        pass
