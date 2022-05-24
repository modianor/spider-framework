from framework.config.config import BaseConfig
from framework.utils.single import Singleton


@Singleton
class ClientConfig(BaseConfig):

    def __init__(self) -> None:
        super().__init__()
        self.configPath = 'client.ini'

    @property
    def section(self):
        return self.config['Client']

    @property
    def TASK_QUEUE_SIZE(self):
        return float(self.section.get('TASK_QUEUE_SIZE', '10'))

    @property
    def Fetch_Interval(self):
        return float(self.section.get('Fetch_Interval', '1'))

    @property
    def VERSION(self):
        return self.section.get('VERSION', '1.0.0')

    @property
    def PROCESS_NAME(self):
        return self.section.get('PROCESS_NAME', 'WIND-ADTSP')

    @property
    def BASE_URL(self):
        return self.section.get('BASE_URL', 'http://spider-framework.com:6048/task')

    @property
    def RESULT_HANDLER_NUM(self):
        return int(self.section.get('RESULT_HANDLER_NUM', '0'))

    @property
    def Fetch_Wait_Interval(self):
        return float(self.section.get('Fetch_Wait_Interval', '3'))

    @property
    def Handle_Task_Interval(self):
        return float(self.section.get('Handle_Task_Interval', '.5'))

    @property
    def Handle_Task_Wait_Interval(self):
        return float(self.section.get('Handle_Task_Wait_Interval', '1'))

    @property
    def PROCESS_LISTEN_PORT(self):
        return int(self.section.get('PROCESS_LISTEN_PORT', '6049'))
