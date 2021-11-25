from config.config import BaseConfig
from utils.single import Singleton


@Singleton
class SpiderConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.configPath = 'spider.ini'
