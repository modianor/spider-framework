import base64
import os
import random
from typing import Tuple

import requests

from core.task import Task
from utils.fileoperator import taskSerialize


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


def uploadTask(task: Task, result: Tuple):
    task_type = task.taskType
    if task_type == 'List' or task_type == 'Data':
        data = {
            'task': str(task),
            'result': str(result[1])
        }
        requests.post(url='http://127.0.0.1:6048/task/uploadTaskParams', data=data)
    elif task_type == 'Detail':
        zipPath = taskSerialize(task, result)
        with open(zipPath, 'rb') as f1:
            base64_str = base64.b64encode(f1.read())  # base64类型
            src = base64_str.decode('utf-8')  # str
        data = {
            'task': str(task),
            'data': str(src)
        }
        response = requests.post(url='http://127.0.0.1:6048/task/uploadTaskData', data=data)
        if response.status_code == 200:
            json_data = response.json()
            if json_data['status'] == 'ok':
                os.remove(zipPath)

    else:
        pass
