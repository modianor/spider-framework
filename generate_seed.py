import json

import requests

from core.task import Task

urlSign = {'url': 'https://tousu.sina.com.cn/api/grp_comp/feed?type=2&page_size=10&page=18&_=1637825891933'}
task = Task(taskId='933467091187531845',
			policyId='HEIMAOTOUSU',
			taskType='List',
			urlSign=json.dumps(urlSign, sort_keys=True),
			companyName='',
			creditCode=''
			)

data = {
	'taskParam': json.dumps(task.__dict__, sort_keys=True)
}
# print(json.dumps(task.__dict__, sort_keys=True))
for i in range(1, 2):
	response = requests.post(url='http://127.0.0.1:6048/task/generateTaskSourceParam', data=data)
	print(response.json())
	# time.sleep(1)
