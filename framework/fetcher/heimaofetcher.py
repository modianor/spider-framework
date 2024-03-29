import json
import traceback
from datetime import datetime

from requests import Session

from framework.core.policy import Policy
from framework.core.task import Task
from framework.fetcher import Fetcher, FetcherStatus
from framework.utils.fileoperator import taskSerialize
from framework.utils.log import Logger
from framework.utils.request_util import MyRequest
from framework.utils.taskpro import taskId


class HeiMaoFetcher(Fetcher):

    def __init__(self) -> None:
        super().__init__()
        self.policyId = 'HEIMAOTOUSU'
        self.logger = Logger(self.policyId.lower()).getlog()
        self.session: Session = Session()
        self.myRequest: MyRequest = MyRequest(self.session, self.logger)
        self.policy = None

    def getList(self, task: Task):
        try:
            self.logger.info(f'List任务 taskId:{task.taskId}, companyName:{task.companyName}')
            json_data = json.loads(task.companyName)
            type_ = json_data['type']
            page_size = json_data['page_size']
            page = json_data['page']
            content = list()
            url = f'https://tousu.sina.com.cn/api/grp_comp/feed?type={type_}&page_size={page_size}&page={page}&_=1637825891933'
            res, resp = self.getContent(url, method='GET')
            if res:
                json_data = resp.json()
                complaints = json_data['result']['data']['list']
                for complaint in complaints:
                    urlSign = {'url': complaint['url']}
                    content.append([urlSign, '', '', f'{self.policyId}|Detail'])
                kibana_log = f'List任务成功, 生成{len(content)}个Detail任务'
                self.logger.info(kibana_log)
                return FetcherStatus.SUCCESS, json.dumps(content, ensure_ascii=False, sort_keys=True), kibana_log
            else:
                kibana_log = f'List任务访问请求失败'
                return FetcherStatus.None_State, '', kibana_log
        except:
            kibana_log = f'List任务处理错误，错误原因:{traceback.format_exc()}'
            self.logger.error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log

    def getDetail(self, task: Task):
        try:
            self.logger.info(f'Detail任务 taskId:{task.taskId}, urlSign:{task.urlSign}')
            json_data = json.loads(task.urlSign)
            url = json_data['url']
            content = list()

            res, resp = self.getContent(url, method='GET')
            if res:
                content.append({'index.html': resp.text})
                info = {
                    'policyId': self.policyId,
                    'taskId': task.taskId,
                    'url': url,
                    'downloadUrl': url,
                    'downloadTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                content.append({'info.txt': json.dumps(info, ensure_ascii=False)})
                kibana_log = f'Detail任务成功'
                self.logger.info(kibana_log)
                return FetcherStatus.SUCCESS, content, kibana_log
            else:
                kibana_log = f'Detail任务失败'
                self.logger.warning(kibana_log)
                return FetcherStatus.FAIL, '', kibana_log
        except:
            kibana_log = f'Detail任务处理错误，错误原因:{traceback.format_exc()}'
            self.logger.error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log

    def getData(self, task: Task):
        try:
            self.logger.info(f'Data任务 taskId:{task.taskId}, urlSign:{task.urlSign}')
            json_data = json.loads(task.urlSign)
            sort_col = json_data['sort_col']
            sort_ord = json_data['sort_ord']
            page_size = json_data['page_size']
            page = json_data['page']
            content = list()
            url = f'https://tousu.sina.com.cn/api/company/main_search?&sort_col={sort_col}&sort_ord={sort_ord}' \
                  f'&page_size={page_size}&page={page}&_=1643421746143'
            res, resp = self.getContent(url, method='GET')
            if res:
                json_data = resp.json()
                lists = json_data['result']['data']['lists']
                for item in lists:
                    uid = item['uid']
                    title = item['title']
                    url = f"https:{item['url']}"
                    content.append({"uid": uid, "title": title, 'url': url})
                kibana_log = f'Data任务成功, 生成{len(content)}个Data任务'
                self.logger.info(kibana_log)
                return FetcherStatus.SUCCESS, json.dumps(content, ensure_ascii=False, sort_keys=True), kibana_log
            else:
                kibana_log = f'Data任务访问请求失败'
                return FetcherStatus.None_State, '', kibana_log
        except:
            kibana_log = f'Data任务处理错误，错误原因:{traceback.format_exc()}'
            self.logger.error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log


if __name__ == '__main__':

    policy = Policy(policyId='HEIMAOTOUSU',
                    proxy=0,
                    interval=0,
                    duplicate=None,
                    timeout=60,
                    retryTimes=3)
    fetcher = HeiMaoFetcher()
    fetcher.setPolicy(policy=policy)

    urlSign = {
        'type': '2',
        'page_size': '10',
        'page': '1'
    }
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
