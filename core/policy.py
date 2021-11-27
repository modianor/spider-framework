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

    def __init__(self, policyId: str, **kwargs) -> None:
        super().__init__()
        self.policyId = policyId
        self.proxy = kwargs['proxy']
        self.interval = kwargs['interval']
        self.duplicate = kwargs['duplicate']
        self.timeout = kwargs['timeout']
        self.retryTimes = kwargs['retryTimes']
        self.taskTypes = kwargs['taskTypes']  # List|Detail|Data
        self.childThreadNum = kwargs['childThreadNum']
        self.kwargs = kwargs
