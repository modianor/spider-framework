import os
import shutil
import stat
import traceback
import zipfile
from os.path import join, exists
from typing import Tuple

from framework.core.task import Task


def delete_file(filePath):
    if os.path.exists(filePath):
        for fileList in os.walk(filePath):
            for name in fileList[2]:
                os.chmod(os.path.join(fileList[0], name), stat.S_IWRITE)
                os.remove(os.path.join(fileList[0], name))
        shutil.rmtree(filePath)


def file2zip(zip_file_name: str, zip_file_dir: str):
    """ 将文件夹中文件压缩存储为zip
    """
    with zipfile.ZipFile(zip_file_name, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        file_names = os.listdir(zip_file_dir)
        for fn in file_names:
            parent_path, name = os.path.split(fn)
            zf.write(join(zip_file_dir, fn), arcname=name)


def createTaskHome(taskId, policyId):
    task_data_dir = getTaskHomePath(taskId, policyId)
    if not exists(path=task_data_dir):
        os.makedirs(name=task_data_dir)


def TaskHomeExist(taskId, policyId):
    task_data_dir = getTaskHomePath(taskId, policyId)
    return os.path.exists(task_data_dir)


def getTaskHomePath(taskId, policyId):
    dir_path = 'Data'
    task_dir = f'{dir_path}/{policyId}'
    task_data_dir = f'{task_dir}/{taskId}'
    return task_data_dir


def getZipPath(taskId, policyId):
    dir_path = 'Data'
    task_dir = f'{dir_path}/{policyId}'
    zip_name = join(task_dir, f'{taskId}.zip')
    return zip_name


def taskSerialize(task: Task, result: Tuple):
    taskStatus, items, _ = result
    policyId = task.policyId
    dir_path = 'Data'
    taskId = task.taskId

    task_dir = f'{dir_path}/{policyId}'
    task_data_dir = f'{task_dir}/{taskId}'
    zip_name = join(task_dir, f'{taskId}.zip')

    if not exists(path=task_data_dir):
        os.makedirs(name=task_data_dir)

    for item in items:
        for name in item:
            value = item[name]
            file_path = join(task_data_dir, name)
            with open(file_path, 'wb') as f:
                try:
                    if isinstance(value, str):
                        value = value.encode('utf-8')
                    f.write(value)
                except:
                    print(traceback.format_exc())

    file2zip(zip_name, task_data_dir)
    delete_file(task_data_dir)
    return zip_name
