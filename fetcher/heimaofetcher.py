import json
from datetime import datetime

import requests

from core.task import Task
from fetcher import Fetcher, FetcherStatus
from utils.fileoperator import taskSerialize
from utils.log import Logger
from utils.taskpro import taskId


class HeiMaoFetcher(Fetcher):

    def __init__(self) -> None:
        super().__init__()
        self.policyId = 'HEIMAOTOUSU'
        self.logger = Logger(self.policyId.lower()).getlog()

    def getList(self, task: Task):
        try:
            self.logger.info(f'List任务参数{task.urlSign}')
            json_data = json.loads(task.urlSign)
            url = json_data['url']
            content = list()
            response = requests.get(url)
            json_data = response.json()
            complaints = json_data['result']['data']['list']
            for complaint in complaints:
                urlSign = {'url': complaint['url']}
                content.append([urlSign, '', '', f'{self.policyId}|Detail'])
            self.logger.info(f'List任务成功, 生成{len(content)}个Detail任务')
            return FetcherStatus.SUCCESS, json.dumps(content, ensure_ascii=False)
        except:
            pass

    def getDetail(self, task: Task):
        try:
            self.logger.info(f'Detail任务参数{task.urlSign}')
            json_data = json.loads(task.urlSign)
            url = json_data['url']
            content = list()

            response = requests.get(url)
            content.append({'index.html': response.text})
            info = {
                'url': url,
                'downloadUrl': url,
                'downloadTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            content.append({'info.txt': json.dumps(info, ensure_ascii=False)})
            self.logger.info(f'Detail任务成功')
            return FetcherStatus.SUCCESS, content
        except:
            pass

    def getData(self, task: Task):
        self.logger.info(task)
        requests.get('https://www.baidu.com')
        return '这是一个Data任务返回结果'


if __name__ == '__main__':
    fetcher = HeiMaoFetcher()

    urlSign = {'url': 'https://tousu.sina.com.cn/api/grp_comp/feed?type=2&page_size=10&page=2&_=1637825891933'}
    task = Task(taskId=taskId(),
                policyId='HEIMOUTOUSU',
                taskType='List',
                urlSign=json.dumps(urlSign, ensure_ascii=False),
                companyName='',
                creditCode=''
                )

    result = fetcher.getList(task)
    taskParams = json.loads(result[1])
    print(result[1])

    for taskParam in taskParams:
        task = Task(taskId=taskId(),
                    policyId='HEIMAOTOUSU',
                    taskType='Detail',
                    urlSign=json.dumps(taskParam[0]),
                    companyName='',
                    creditCode=''
                    )
        result = fetcher.getDetail(task)
        taskSerialize(task, result)
