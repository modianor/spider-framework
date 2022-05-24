import json

from framework.core.task import Task


def contextParse(task: Task):
    pass


def initContext(task: Task):
    # 上下文容器
    context = {}
    policyId = task.policyId
    taskType = task.taskType
    urlSign = json.loads(task.urlSign)
    commonConfig = json.loads(task.companyName)
    if taskType == 'List':
        urlTemp = commonConfig.get("url", "")
        context['policyId'] = policyId
        context['urlSign'] = urlSign
        context['config'] = commonConfig
        context['urlTemp'] = urlTemp
    elif taskType == 'Detail' or taskType == 'List':
        context['policyId'] = policyId
        context['urlSign'] = urlSign
        context['config'] = commonConfig
    return context
