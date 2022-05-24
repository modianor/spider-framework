from http.server import HTTPServer
from threading import Thread

from framework.config import Client
from framework.core import logger
from framework.core.schedule import Scheduler
from framework.utils.httpinterface import SpiderHttpHandler
from framework.utils.single import Singleton


@Singleton
class Spider(object):
    def __init__(self) -> None:
        logger.info(f'{"=" * 10}爬虫进程开始初始化{"=" * 10}')
        self.processName = Client.PROCESS_NAME
        self.VERSION = Client.VERSION
        self.scheduler = Scheduler()

    def httpServerInit(self):
        host = ('127.0.0.1', Client.PROCESS_LISTEN_PORT)
        server = HTTPServer(host, SpiderHttpHandler)
        logger.info("Starting server, listen at: %s:%s" % host)
        server.serve_forever()

    def init(self):
        httpThread = Thread(target=self.httpServerInit, args=())
        httpThread.start()

        self.scheduler.initSchedule()
        logger.info(f'{"=" * 10}爬虫进程初始化完成{"=" * 10}')
