import json

from framework.core.task import Task


def contextParse(task: Task):
    pass


def initContext(task: Task):
    # 上下文容器
    context = {}
    policyId = task.policyId
    taskType = task.taskType
    taskId = task.taskId
    urlSign = json.loads(task.urlSign)
    commonConfig = json.loads(task.companyName)
    if taskType == 'List' or taskType == 'Data':
        urlTemp = commonConfig.get("url", "")
        context['taskId'] = taskId
        context['policyId'] = policyId
        context['urlSign'] = urlSign
        context['config'] = commonConfig
        context['urlTemplate'] = urlTemp
    elif taskType == 'Detail':
        context['taskId'] = taskId
        context['policyId'] = policyId
        context['urlSign'] = urlSign
        context['config'] = commonConfig
    return context
