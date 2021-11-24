import json
import logging

import requests

from core.task import Task
from fetcher import Fetcher, FetcherStatus

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s:%(lineno)d] %(levelname)s: %(message)s')


class HeiMaoFetcher(Fetcher):

	def __init__(self) -> None:
		super().__init__()
		self.policyId = 'HEIMAOTOUSU'
		self.logger = logging.getLogger(__name__)

	def getList(self, task: Task):
		response = requests.get('https://www.baidu.com')
		content = list()
		taskParam = ['urlSign', 'companyName', 'creditCode', f'{self.policyId}|Detail']
		content.append(json.dumps(taskParam, ensure_ascii=False))
		return FetcherStatus.SUCCESS, content

	def getDetail(self, task: Task):
		requests.get('https://www.baidu.com')
		return '这是一个Detail任务返回结果'

	def getData(self, task: Task):
		requests.get('https://www.baidu.com')
		return '这是一个Data任务返回结果'
