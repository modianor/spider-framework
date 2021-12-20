import json
from typing import List


class Policy(object):
    # 业务配置类

    # 业务策略名称
    # 消重服务
    # 是否启用代理
    # 每次请求间隔
    # 请求超时时间
    # 请求重试次数
    # 策略持有的任务类型List|Detail|Data
    # 策略对应插件的子线程(默认为0)
    # 策略对应插件的子线程任务队列上限(默认为1)

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.policyId = kwargs.get('policyId', '')
        self.policyName = kwargs.get('policyName', '')
        self.policyState = kwargs.get('policyState', False)
        self.proxy = kwargs.get('proxy', 0)
        self.interval = kwargs.get('interval', 0)
        # self.duplicate = kwargs.get('duplicate', 'duplicate_server_1')
        self.timeout = kwargs.get('timeout', 60)
        self.retryTimes = kwargs.get('retryTimes', 3)
        self.taskQueueSize = kwargs.get('taskQueueSize', 1)
        self.childThreadNum = kwargs.get('childThreadNum', 0)
        self.taskTypesInfo = kwargs.get('taskTypesInfo', 'List|Detail|Data')  # List|Detail|Data
        self.kwargs = kwargs

    @property
    def taskTypes(self) -> List[str]:
        return self.taskTypesInfo.split('|')

    def __str__(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)
