class Task(object):
    def __init__(self, taskId=0, policyId='', taskType='', urlSign='', companyName='', creditCode='', **kwargs) -> None:
        super().__init__()
        # from utils import taskpro
        self.taskId = taskId
        self.policyId = policyId
        self.taskType = taskType
        self.urlSign = urlSign
        self.companyName = companyName
        self.creditCode = creditCode
        # 策略工作模式
        self.policyMode = kwargs.get('policyMode', 'plugin')
        self.in_progress_time = kwargs.get('in_progress_time', '')
        self.parentTaskId = kwargs.get('parentTaskId', '')

    def __str__(self) -> str:
        return str(self.__dict__)

    @classmethod
    def fromJson(cls, **kwargs):
        return cls(**kwargs)


if __name__ == '__main__':
    task = Task(
        taskId=5435354356346,
        policyId='HEIMAOTOUSU',
        taskType='List',
        urlSign='',
        companyName='',
        creditCode=''
    )

    print(task)
