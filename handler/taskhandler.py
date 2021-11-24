import logging
import time
from threading import Thread
from typing import Dict, List

from core.task import Task
from fetcher import Fetcher
from handler import BaseHandler
from utils.cls_loader import load_object
from utils.config import PluginConfig
from utils.single import Singleton
from utils.spiderqueue import TaskQueue, ResultQueue


class FetcherThread(Thread):

	def __init__(self, policyId, fetcherInstance: Fetcher, policyTaskQueue: TaskQueue, resultQueue: ResultQueue,
				 threadName: str, **kwds):
		Thread.__init__(self, **kwds)
		self.logger = logging.getLogger('spider.TaskHandler.FetcherThread')
		self.policyId = policyId
		self.close = False
		self.fetcherInstance = fetcherInstance
		self.policyTaskQueue = policyTaskQueue
		self.resultQueue = resultQueue
		self.threadName = threadName
		self.parentThread = None
		self.childThreadNum = 0
		self.childThreads: List[FetcherThread] = list()
		self.logger.info(f'{self.threadName} start')

	def __checkChildThreads__(self):
		if 'ParentThread' in self.threadName:
			if len(self.childThreads) == self.childThreadNum:
				pass
			elif len(self.childThreads) < self.childThreadNum:
				# 需要添加子线程
				deltaThreadNum = self.childThreadNum - len(self.childThreads)
				for i in range(deltaThreadNum):
					childThread = FetcherThread(self.policyId, self.fetcherInstance, self.policyTaskQueue,
												f'{self.policyId}_ChildThread_{i + 1}')
					self.childThreads.append(childThread)
				for childThread in self.childThreads:
					childThread.start()
			else:
				# 需要删除子线程
				deltaThreadNum = len(self.childThreads) - self.childThreadNum
				for i in range(deltaThreadNum):
					childThread = self.childThreads[len(self.childThreads) - 1]
					self.childThreads.remove(childThread)
					childThread.modifyClose()

	def run(self) -> None:
		while True:
			if not self.close:
				self.__checkChildThreads__()
				if not self.policyTaskQueue.isEmpty():
					self.logger.info(f'{self.threadName} handler a task')
					task = self.policyTaskQueue.getTask()
					taskType = task.taskType
					if taskType == 'List':
						# (taskStatus,[[urlSign, companyName, creditCode,#{policyId}:{taskType}#]],kibanalog)
						result = self.fetcherInstance.getList(task)
					elif taskType == 'Detail':
						# (taskStatus,{k1:v1, k2:v2, k3:v3}],kibanalog)
						result = self.fetcherInstance.getDetail(task)
					elif taskType == 'Data':
						# (taskStatus,{k1:v1, k2:v2, k3:v3}],kibanalog)
						result = self.fetcherInstance.getData(task)
					self.resultQueue.putResult(result)
				else:
					time.sleep(1)
			else:
				self.logger.warning(f'{self.threadName} release')
				break

	def modifyClose(self):
		self.close = True


@Singleton
class TaskHandler(BaseHandler):
	def __init__(self, resultQueue: ResultQueue) -> None:
		self.logger = logging.getLogger('spider.TaskHandler')
		self.policyHandler: Dict[str, FetcherThread] = dict()
		self.policyTaskQueues: Dict[str, TaskQueue] = dict()
		self.resultQueue = resultQueue
		self.loadFetchers()
		self.logger.info('TaskHandler start')

	def loadFetchers(self):
		config = PluginConfig()
		plugins: Dict = config.plugins
		for policyId in plugins:
			module = plugins[policyId]
			fetcher = load_object(module)()
			self.logger.info(f'load {module} successfully')

			taskQueue = TaskQueue()
			self.policyTaskQueues[policyId] = taskQueue
			self.policyHandler[policyId] = FetcherThread(policyId=policyId, fetcherInstance=fetcher,
														 policyTaskQueue=taskQueue,
														 resultQueue=self.resultQueue,
														 threadName=f'{policyId}_ParentThread')

		for policyId in self.policyHandler:
			policyIdThread = self.policyHandler[policyId]
			policyIdThread.start()

	def handle(self, task: Task):
		policyId = task.policyId
		policyTaskQueue = self.policyTaskQueues[policyId]
		if policyTaskQueue.size() < 10:
			self.policyTaskQueues[policyId].putTask(task)
			return True
		else:
			self.logger.warning(f'policyId:{policyId} policyTaskQueue is full')
			return False
