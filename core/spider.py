from config import Client
from core import logger
from core.schedule import Scheduler
from utils.single import Singleton


@Singleton
class Spider(object):
    def __init__(self) -> None:
        logger.info(f'{"=" * 10}爬虫进程开始初始化{"=" * 10}')
        self.processName = Client.PROCESS_NAME
        self.VERSION = Client.VERSION
        self.scheduler = Scheduler()

    def start(self):
        self.scheduler.run = True
        logger.info(f'爬虫进程:{self.processName} 版本:{self.VERSION} 开始调度')

    def pause(self):
        self.scheduler.run = False
        logger.info(f'爬虫进程:{self.processName} 版本:{self.VERSION} 停止调度')

    def init(self):
        self.scheduler.initSchedule()
        logger.info(f'{"=" * 10}爬虫进程初始化完成{"=" * 10}')
