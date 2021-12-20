import json
import time

import requests

from core.task import Task
from utils.taskpro import taskId

urlSign = {'url': 'https://tousu.sina.com.cn/api/grp_comp/feed?type=2&page_size=10&page=2&_=1637825891933'}
task = Task(taskId=taskId(),
            policyId='HEIMAOTOUSU',
            taskType='List',
            urlSign=json.dumps(urlSign, ensure_ascii=False),
            companyName='',
            creditCode=''
            )

data = {
    'taskParam': str(task)
}

for i in range(1, 100):
    response = requests.post(url='http://127.0.0.1:6048/task/generateTaskParam', data=data)
    print(response.json())
    # time.sleep(1)
