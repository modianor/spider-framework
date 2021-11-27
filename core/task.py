class Task(object):
    def __init__(self, taskId=0, policyId='', taskType='', urlSign='', companyName='', creditCode='', **kwargs) -> None:
        super().__init__()
        self.taskId = taskId
        self.policyId = policyId
        self.taskType = taskType
        self.urlSign = urlSign
        self.companyName = companyName
        self.creditCode = creditCode

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
