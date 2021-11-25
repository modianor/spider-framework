from config.config import BaseConfig
from utils.single import Singleton


@Singleton
class ClientConfig(BaseConfig):

    def __init__(self) -> None:
        super().__init__()
        self.configPath = 'client.ini'

    @property
    def section(self):
        return self.config['Client']

    @property
    def TASKQUEUE_SZIE(self):
        return int(self.section.get('TASKQUEUE_SIZE', '10'))

    @property
    def Fetch_Interval(self):
        return int(self.section.get('Fetch_Interval', '1'))

    @property
    def VERSION(self):
        return self.section.get('VERSION', '1.0.0')

    @property
    def PROCESS_NAME(self):
        return self.section.get('PROCESS_NAME', 'WIND-ADTSP')

    @property
    def BASE_URL(self):
        return self.section.get('BASE_URL', 'https://spider-framework.com:8096')

    @property
    def RESULT_HANDLER_NUM(self):
        return int(self.section.get('RESULT_HANDLER_NUM', '0'))
