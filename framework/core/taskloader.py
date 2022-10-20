"""
 任务加载器
 作用为爬虫进程下面的策略插件加载任务参数
 加载器需要自动维护爬虫任务参数队列，并对
 插件线程暴露调用接口。目前任务参数加载器
 暂时的加载策略是当前任务参数队列没有对应
 活跃爬虫策略的任务参数时，去爬虫服务平台
 获取对应的策略任务参数。何为活跃的爬虫任
 务策略？即爬虫进程plugins中启用的策略ID
 和爬虫管理平台中主机进程配置中启用的策略ID
 的交集
"""
import time
from typing import Dict
from urllib.parse import urljoin

import requests

from framework.config import Client
from framework.core import logger
from framework.core.policy import Policy
from framework.core.task import Task
from framework.utils.single import Singleton


@Singleton
class TaskLoader(object):
    def __init__(self):
        self.logger = logger
        self.policies = dict()
        self.taskSlot = dict()

    def updatePolicies(self, policies: Dict[str, Policy or None]):
        """
        更新任务加载器处理的策略
        Args:
            policies: 策略ID和策略对象

        Returns: None

        """
        self.policies = policies

    def getTaskByPolicyId(self, policyId):
        """

        Args:
            policyId:

        Returns:

        """
        task = self.taskSlot.get(policyId, None)
        self.taskSlot[policyId] = None
        return task

    def supplyPolicyTasks(self):
        try:
            policyIds = self.getActivePolicyIds()
            if len(policyIds) == 0:
                return

            self.logger.info(f'正在尝试获取任务:{";".join(policyIds)}')
            data = {'policyIds': policyIds, 'processName': Client.PROCESS_NAME}
            url = urljoin(Client.BASE_URL, './getTaskParams')
            response = requests.post(url=url, data=data)
            task_params = response.json()

            if len(task_params) == 0:
                self.logger.warning("爬虫进程获取任务为空")
                time.sleep(Client.Fetch_Interval * 5)

            for task_param in task_params:
                try:
                    task = Task.fromJson(**task_param)
                    policyId = task.policyId
                    policyMode = task.policyMode
                    if policyMode == 'config':
                        policyId = 'NORMAL'
                    self.taskSlot[policyId] = task
                except TypeError:
                    self.logger.warning('爬虫进程反序列化任务出错')
        except:
            self.logger.error('spider taskloader fail to get tasks ...')

    def getActivePolicyIds(self):
        policyIds = list()
        for policyId in self.policies:
            policy = self.policies[policyId]
            if policy is None:
                continue
            if (policy.taskTypesInfo is None or policy.taskTypesInfo == '') and policy.policyId != 'NORMAL':
                continue

            if not self.isTaskEmpty(policyId):
                continue
            taskParams = f'{policy.policyId}:{"|".join(policy.taskTypes)}'
            policyIds.append(taskParams)
        return policyIds

    def isTaskEmpty(self, policyId):
        if self.taskSlot.get(policyId, None) is None:
            return True
        else:
            return False
