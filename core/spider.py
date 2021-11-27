from config import Client
from core import logger
from core.schedule import Scheduler


class Spider(object):
    def __init__(self) -> None:
        logger.info(f'{"=" * 10}爬虫进程开始初始化{"=" * 10}')
        self.processName = Client.PROCESS_NAME
        self.VERSION = Client.VERSION
        self.scheduler = Scheduler()

    def start(self):
        pass

    def pause(self):
        pass

    def getPolicyInfos(self):
        pass

    def init(self):
        self.scheduler.initSchedule()
        logger.info(f'{"=" * 10}爬虫进程初始化完成{"=" * 10}')
