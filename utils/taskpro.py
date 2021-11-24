import random

from core.task import Task


def taskId():
    return int(str(random.random())[2:12])


def randomTask():
    taskTypes = ['List', 'Detail', 'Data']
    policyIds = ['HEIMAOTOUSU']
    task = Task(
        taskId=taskId(),
        policyId=random.choice(policyIds),
        taskType=random.choice(taskTypes),
        urlSign='',
        companyName='',
        creditCode=''
    )
    return task
