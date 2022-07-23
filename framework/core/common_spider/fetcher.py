import json
import traceback
from datetime import datetime

from requests import Session

from framework.core.common_spider.context_parse import initContext
from framework.core.common_spider.page_download import PageDownloader
from framework.core.common_spider.page_turn import PageTurner
from framework.core.task import Task
from framework.fetcher import Fetcher, FetcherStatus
from framework.utils.log import Logger
from framework.utils.request_util import MyRequest


class NormalFetcher(Fetcher):

    def __init__(self) -> None:
        super().__init__()
        self.policyId = 'NORMAL'
        self.logger = Logger(self.policyId.lower()).getlog()
        self.session: Session = Session()
        self.myRequest: MyRequest = MyRequest(self.session, self.getCurrentLogger(policyId=self.policyId))
        self.policy = None

    def getCurrentLogger(self, policyId='normal'):
        return Logger(policyId).getlog()

    def updatePolicy(self, task: Task):
        # policys = getPolicy([task.policyId])
        # for policy in policys:
        #     self.myRequest.update(self.session, self.getCurrentLogger(policyId=policy.policyId.lower()))
        #     self.setPolicy(policy=policy)
        self.myRequest.update(self.session, self.getCurrentLogger(policyId=task.policyId.lower()))

    def getDetail(self, task: Task):
        try:
            self.updatePolicy(task)
            self.getCurrentLogger(task.policyId.lower()).info(
                f'通用配置爬虫正在处理 taskId:{task.taskId}, policyId:{task.policyId}, Detail任务参数:{task.urlSign}')
            context = initContext(task=task)
            urlSign = context.get('urlSign')
            config = context.get('config')
            url = urlSign.get('url')
            context['url'] = url
            PageDownloader.downloadDetailFile(self.getContent, url, context,
                                              self.getCurrentLogger(policyId=task.policyId.lower()))
            content = context.get('detail_down', [])
            info = {
                'policyId': task.policyId,
                'taskId': task.taskId,
                'url': url,
                'downloadUrl': url,
                'downloadTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            info.update(urlSign)
            content.append({'info.txt': json.dumps(info, ensure_ascii=False)})

            if len(content) > 1:
                kibana_log = f'Detail任务 taskId:{task.taskId}, policyId:{task.policyId} 成功'
                self.getCurrentLogger(task.policyId.lower()).info(kibana_log)
                return FetcherStatus.SUCCESS, content, kibana_log
            else:
                kibana_log = f'Detail任务 taskId:{task.taskId}, policyId:{task.policyId} 失败'
                self.getCurrentLogger(task.policyId.lower()).warning(kibana_log)
                return FetcherStatus.FAIL, '', kibana_log
        except:
            kibana_log = f'Detail任务 taskId:{task.taskId}, policyId:{task.policyId} 处理错误，错误原因:{traceback.format_exc()}'
            self.getCurrentLogger(task.policyId.lower()).error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log

    def getList(self, task: Task):
        try:
            self.updatePolicy(task)
            policyId = task.policyId
            content = []
            self.getCurrentLogger(task.policyId.lower()).info(
                f'通用配置爬虫正在处理 taskId:{task.taskId}, policyId:{task.policyId}, List任务参数:{task.urlSign}')
            # 上下文容器
            context = initContext(task=task)
            params = PageTurner(self.getContent).turnPage(context, configType='list')
            for param in params:
                content.append([json.dumps(param, ensure_ascii=False), '', '', f'{policyId}|Detail'])

            kibana_log = f'List任务 taskId:{task.taskId}, policyId:{task.policyId} 成功, 生成{content}个Detail任务'
            self.getCurrentLogger(task.policyId.lower()).info(kibana_log)
            return FetcherStatus.SUCCESS, json.dumps(content, ensure_ascii=False,
                                                     sort_keys=True), kibana_log
        except:
            kibana_log = f'List任务 taskId:{task.taskId}, policyId:{task.policyId} 处理错误，错误原因:{traceback.format_exc()}'
            self.getCurrentLogger(task.policyId.lower()).error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log

    def getData(self, task: Task):
        try:
            self.updatePolicy(task)
            self.getCurrentLogger(task.policyId.lower()).info(
                f'通用配置爬虫正在处理 policyId:{task.policyId}, Data任务参数:{task.urlSign}')
            # 上下文容器
            context = initContext(task=task)
            params = PageTurner(self.getContent).turnPage(context, configType='data')
            kibana_log = f'Data任务 taskId:{task.taskId}, policyId:{task.policyId} 成功, 生成{params}个Data任务'
            self.getCurrentLogger(task.policyId.lower()).info(kibana_log)
            return FetcherStatus.SUCCESS, json.dumps(params, ensure_ascii=False,
                                                     sort_keys=True), kibana_log
        except:
            kibana_log = f'Data任务 taskId:{task.taskId}, policyId:{task.policyId} 处理错误，错误原因:{traceback.format_exc()}'
            self.getCurrentLogger(task.policyId.lower()).error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log
