import base64
import json
import os
import random
import time
from os.path import exists
from typing import Tuple

import requests

from framework.core.task import Task
from framework.utils.fileoperator import taskSerialize, getZipPath

FILE_PART_SIZE = 1024 * 1024 * 5


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
        # 判断zip文件大小是否超过分包阈值
        zip_size = os.path.getsize(zipPath)

        if zip_size <= 1024 * 1024 * 5:
            # 文件大小低于分包阈值 直接以base64编码传递给后端
            uploadByBase64(task, result)
        else:
            # 文件大小高于分包阈值 需要对zip文件进行分包 以文件的方式传递给后端
            uploadBySliceFile(task, result)
    else:
        pass


def getTaskPartHomePath(taskId, policyId):
    dir_path = 'Data'
    task_dir = f'{dir_path}/{policyId}'
    task_data_dir = f'{task_dir}/{taskId}_part'
    return task_data_dir


def createTaskPartHome(taskId, policyId):
    task_data_dir = getTaskPartHomePath(taskId, policyId)
    if not exists(path=task_data_dir):
        os.makedirs(name=task_data_dir)


def sliceFile(task: Task):
    taskId, policyId = task.taskId, task.policyId
    file_name = f'{taskId}.zip'
    file_size = os.path.getsize(file_name)
    createTaskPartHome(taskId, policyId)
    taskPartHome = getTaskPartHomePath(taskId, policyId)
    with open(file_name, 'rb') as f:
        part_nums = (file_size + FILE_PART_SIZE - 1) // FILE_PART_SIZE
        for i in range(part_nums):
            seek_len = i * FILE_PART_SIZE
            f.seek(seek_len)
            part_data = f.read(FILE_PART_SIZE)
            part_file_name = f'{taskId}_{i + 1}_{part_nums}.part'
            part_file_path = f'{taskPartHome}/{part_file_name}'
            with open(part_file_path, 'wb') as fw:
                fw.write(part_data)


def sendPartFile(task: Task, result: Tuple):
    taskId, policyId = task.taskId, task.policyId
    file_name = f'{taskId}.zip'
    taskPartHome = getTaskPartHomePath(taskId, policyId)
    part_file_names = os.listdir(taskPartHome)
    part_file_names.sort()
    for i, part_file_name in enumerate(part_file_names):
        part_file_path = f'{taskPartHome}/{part_file_name}'
        prefix_name = part_file_name.split('.')[0]
        infos = prefix_name.split('_')
        chunkNumber = infos[1]
        totalChunks = infos[2]
        with open(part_file_path, 'rb') as fr:
            data = {
                'taskId': taskId,
                'policyId': policyId,
                'bisName': policyId,
                'chunkNumber': chunkNumber,
                'totalChunks': totalChunks,
                'filename': file_name,
                'task': json.dumps(task.__dict__, sort_keys=True),
                'status': result[0],
                'kibana_log': result[2] if result[2] else '',
            }

            files = {'file': fr}
            url = 'http://spider-framework:6048/task/uploadTaskChunkParams'
            for _ in range(5):
                response = requests.post(url, files=files, data=data)
                if response.status_code == 200:
                    json_data = response.json()
                    if json_data['status'] == 'ok':
                        os.remove(part_file_path)
                        break
                time.sleep(1)


def uploadByBase64(task: Task, result: Tuple):
    zipPath = getZipPath(task.taskId, task.policyId)
    with open(zipPath, 'rb') as f1:
        base64_str = base64.b64encode(f1.read())  # base64类型
        src = base64_str.decode('utf-8')  # str
    data = {
        'task': json.dumps(task.__dict__, sort_keys=True),
        'status': int(result[0]),
        'result': str(src),
        'kibana_log': result[2] if result[2] else ''
    }
    for _ in range(5):
        response = requests.post(url='http://spider-framework:6048/task/uploadTaskParams', data=data)
        if response.status_code == 200:
            json_data = response.json()
            if json_data['status'] == 'ok':
                os.remove(zipPath)
                break
        time.sleep(1)


def uploadBySliceFile(task: Task, result: Tuple):
    sliceFile(task)
    sendPartFile(task, result)
