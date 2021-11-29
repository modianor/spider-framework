import json
import traceback
from datetime import datetime

from requests import Session

from core.policy import Policy
from core.task import Task
from fetcher import Fetcher, FetcherStatus
from utils.fileoperator import taskSerialize
from utils.log import Logger
from utils.request_util import MyRequest
from utils.taskpro import taskId


class HeiMaoFetcher(Fetcher):

    def __init__(self) -> None:
        super().__init__()
        self.policyId = 'HEIMAOTOUSU'
        self.logger = Logger(self.policyId.lower()).getlog()
        self.session: Session = Session()
        self.myRequest: MyRequest = MyRequest(self.session, self.logger)
        self.policy = None

    def getContent(self, url, params=None, data=None, headers=None, method='GET'):
        res, resp = self.myRequest.getContent(url=url,
                                              method=method,
                                              params=params,
                                              headers=headers,
                                              data=data,
                                              timeout=self.policy.timeout,
                                              retryTimes=self.policy.retryTimes,
                                              interval=self.policy.interval,
                                              proxy=self.policy.proxy)

        return res, resp

    def getList(self, task: Task):
        try:
            self.logger.info(f'List任务参数{task.urlSign}')
            json_data = json.loads(task.urlSign)
            url = json_data['url']
            content = list()
            res, resp = self.getContent(url, method='GET')
            if res:
                json_data = resp.json()
                complaints = json_data['result']['data']['list']
                for complaint in complaints:
                    urlSign = {'url': complaint['url']}
                    content.append([urlSign, '', '', f'{self.policyId}|Detail'])
                self.logger.info(f'List任务成功, 生成{len(content)}个Detail任务')
                return FetcherStatus.SUCCESS, json.dumps(content, ensure_ascii=False)
            else:
                return FetcherStatus.None_State, ''
        except:
            self.logger.error(traceback.format_exc())
            return FetcherStatus.FAIL, ''

    def getDetail(self, task: Task):
        try:
            self.logger.info(f'Detail任务参数{task.urlSign}')
            json_data = json.loads(task.urlSign)
            url = json_data['url']
            content = list()

            res, resp = self.getContent(url, method='GET')
            if res:
                content.append({'index.html': resp.text})
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
        pass


if __name__ == '__main__':

    policy = Policy(policyId='HEIMAOTOUSU',
                    proxy=0,
                    interval=0,
                    duplicate=None,
                    timeout=60,
                    retryTimes=3)
    fetcher = HeiMaoFetcher()
    fetcher.setPolicy(policy=policy)

    urlSign = {'url': 'https://tousu.sina.com.cn/api/grp_comp/feed?type=2&page_size=10&page=2&_=1637825891933'}
    task = Task(taskId=taskId(),
                policyId='HEIMOUTOUSU',
                taskType='List',
                urlSign=json.dumps(urlSign, ensure_ascii=False),
                companyName='',
                creditCode=''
                )

    result = fetcher.getList(task)

    if result[0]:
        taskParams = json.loads(result[1])
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
