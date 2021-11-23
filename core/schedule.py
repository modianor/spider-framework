import time
from typing import Dict

from core.task import Task
from utils.cls_loader import load_object
from utils.config import PluginConfig
from utils.single import singleton
from utils.taskqueue import TaskQueue


@singleton
class Scheduler(object):
	def __init__(self) -> None:
		self.run = False
		self.task_queue = TaskQueue()
		self.fetchers = dict()
		self.load_fetchers()

	def print_status(self):
		while True:
			print('Scheduler is run: ', self.run)
			time.sleep(1)

	def get_task(self):
		while True:
			if self.run:
				task = Task(
					taskId=5435354356346,
					policyId='HEIMAOTOUSU',
					taskType='List',
					urlSign='',
					companyName='',
					creditCode=''
				)

				self.task_queue.put(task)
				time.sleep(1)

	def handle_task(self):
		task = self.task_queue.get()

		policyId = task.policyId
		taskType = task.taskType

		spec_fetcher = self.fetchers[policyId]
		if taskType == 'List':
			result = spec_fetcher.getList(task)
		elif taskType == 'Detail':
			result = spec_fetcher.getDetail(task)
		elif taskType == 'Detail':
			result = spec_fetcher.getData(task)

	def load_fetchers(self):
		config = PluginConfig()
		plugins: Dict = config.plugins
		for policyId in plugins:
			module = plugins[policyId]
			self.fetchers[policyId] = load_object(module)()
