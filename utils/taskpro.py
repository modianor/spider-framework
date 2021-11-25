import random

from core.task import Task


def taskId():
    return int(str(random.random())[2:12])


def randomTask():
    taskTypes = ['List']
    policyIds = ['HEIMAOTOUSU']
    task = Task(
        taskId=taskId(),
        policyId=random.choice(policyIds),
        taskType=random.choice(taskTypes),
        urlSign='{"url": "https://tousu.sina.com.cn/api/grp_comp/feed?type=2&page_size=10&page=2&_=1637825891933"}',
        companyName='',
        creditCode=''
    )
    return task
