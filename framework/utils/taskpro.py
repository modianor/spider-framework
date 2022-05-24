import base64
import json
import os
import random
from typing import Tuple

import requests

from framework.core.task import Task
from framework.utils.fileoperator import taskSerialize


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
            'task': json.dumps(task.__dict__, sort_keys=True),
            'status': int(result[0]),
            'result': str(result[1]),
            'kibana_log': result[2] if result[2] else ''
        }
        requests.post(url='http://spider-framework:6048/task/uploadTaskParams', data=data)
    elif task_type == 'Detail':
        zipPath = taskSerialize(task, result)
        with open(zipPath, 'rb') as f1:
            base64_str = base64.b64encode(f1.read())  # base64类型
            src = base64_str.decode('utf-8')  # str
        data = {
            'task': json.dumps(task.__dict__, sort_keys=True),
            'status': int(result[0]),
            'result': str(src),
            'kibana_log': result[2] if result[2] else ''
        }
        response = requests.post(url='http://spider-framework:6048/task/uploadTaskParams', data=data)
        if response.status_code == 200:
            json_data = response.json()
            if json_data['status'] == 'ok':
                os.remove(zipPath)

    else:
        pass
