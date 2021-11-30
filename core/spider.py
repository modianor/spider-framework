from threading import Thread

import uvicorn
from fastapi import FastAPI

from config import Client
from core import logger
from core.schedule import Scheduler
from utils.single import Singleton


@Singleton
class Spider(object):
    app = FastAPI()  # 必须实例化该类，启动的时候调用

    def __init__(self) -> None:
        logger.info(f'{"=" * 10}爬虫进程开始初始化{"=" * 10}')
        self.processName = Client.PROCESS_NAME
        self.VERSION = Client.VERSION
        self.scheduler = Scheduler()

    def httpServer(self):
        uvicorn.run(app=self.app, host="127.0.0.1", port=Client.PROCESS_LISTEN_PORT)

    @staticmethod
    @app.get('/spider/start')
    def start():
        scheduler = Scheduler()
        scheduler.run = True
        logger.info(f'爬虫进程:{Client.PROCESS_NAME} 版本:{Client.VERSION} 开始调度')
        return {'success': True, 'status': True}

    @staticmethod
    @app.get('/spider/pause')
    def pause():
        scheduler = Scheduler()
        scheduler.run = False
        logger.info(f'爬虫进程:{Client.PROCESS_NAME} 版本:{Client.VERSION} 停止调度')
        return {'success': True, 'status': False}

    def init(self):
        self.scheduler.initSchedule()

        httpThread = Thread(target=self.httpServer, args=())
        httpThread.start()
        logger.info(f'{"=" * 10}爬虫进程初始化完成{"=" * 10}')
