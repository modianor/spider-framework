import json
import re
import time
import traceback
from datetime import datetime

import redis
from requests import Session
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from framework.core.policy import Policy
from framework.core.task import Task
from framework.fetcher import Fetcher, FetcherStatus
from framework.utils.fileoperator import taskSerialize
from framework.utils.log import Logger
from framework.utils.request_util import MyRequest
from framework.utils.taskpro import taskId
from framework.utils.webdriver_util import WebDriverUtil


class SBJFetcher(Fetcher):

    def __init__(self) -> None:
        super().__init__()
        self.policyId = 'SBJ'
        self.logger = Logger(self.policyId.lower()).getlog()
        self.session: Session = Session()
        self.myRequest: MyRequest = MyRequest(self.session, self.logger)
        self.policy = None
        self.driver = None
        self.detail_driver = None
        self.num = 0
        self.redis_client = redis.Redis(host='192.168.24.5', port=6379, db=1, decode_responses=True)

    def generate_options(self):
        result = self.redis_client.zrangebyscore("proxies", 10, 10)

    def getList(self, task: Task):
        try:
            self.logger.info(f'List任务 taskId:{task.taskId}, urlSign:{task.urlSign}')
            json_data = json.loads(task.urlSign)
            url = json_data['url']
            pageStart = int(json_data['pageStart'])
            pageEnd = int(json_data['pageEnd'])
            content = list()

            self.createHomePage(url)

            if pageEnd - pageStart + 1 <= 5:
                input = self.driver.find_element(By.XPATH, '//*[@id="pages"]/table/tbody/tr/td[5]/input')
                input.clear()
                input.send_keys(pageStart)
                input.send_keys(Keys.ENTER)
                self.judgeTurnPage()

                all_items = []
                for i in range(pageStart, pageEnd):
                    while True:
                        html = self.driver.execute_script("return document.documentElement.outerHTML")
                        if '正在加载信息...' in html:
                            print('正在加载信息...')
                            time.sleep(.1)
                        else:
                            items = re.findall('toImg\\(&quot;(\\d+)&quot;,&quot;(\\d+)&quot;,&quot;(.*?)&quot;\\);',
                                               html)
                            all_items.extend(items)
                            button = self.driver.find_element(By.XPATH,
                                                              '//*[@id="pages"]/table/tbody/tr/td[8]/a/span/span[2]')
                            button.click()
                            time.sleep(.2)
                            break

                for item in all_items:
                    data = {
                        'url': 'http://wsgg.sbj.cnipa.gov.cn:9080/tmann/annInfoView/annSearch.html?annNum=1805',
                        'ann_num': item[0],
                        'page_no': item[1],
                        'ann_type_code': item[2]
                    }
                    content.append([json.dumps(data, ensure_ascii=False), '', '', f'{self.policyId}|Detail'])

                if len(content) > 0:
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
        finally:
            WebDriverUtil.closeWebDriver(self.policyId, self.driver)

    def getDetail(self, task: Task):
        try:
            self.logger.info(f'Detail任务 taskId:{task.taskId}, urlSign:{task.urlSign}')
            json_data = json.loads(task.urlSign)
            url_ = json_data['url']
            ann_num = json_data['ann_num']
            page_no = json_data['page_no']
            ann_type_code = json_data['ann_type_code']
            content = list()
            if self.detail_driver is None or self.num % 50 == 0:
                self.createDetailPage(url_)

            for _ in range(5):
                self.num = self.num + 1
                js_code = f'toImg("{ann_num}", "{page_no}", "{ann_type_code}");'
                self.detail_driver.execute_script(js_code)
                load_complete = False
                while True:
                    try:
                        if load_complete:
                            break
                        time.sleep(.1)
                        self.detail_driver.switch_to.alert.accept()
                        load_complete = True
                    except:
                        pass

                reques_obj = self.detail_driver.execute_script("return localStorage.getItem('contentUrlData');")
                self.detail_driver.execute_script("$('#imageview').window('close');")
                reques_obj = json.loads(reques_obj)
                url = reques_obj['url']
                data = {
                    'flag': reques_obj['requestBody']['formData']['flag'][0],
                    'id': reques_obj['requestBody']['formData']['id'][0],
                    'pageNum': reques_obj['requestBody']['formData']['pageNum'][0]
                }
                cookie_str = self.detail_driver.execute_script("return localStorage.getItem('contentCookieData');")
                cookies = json.loads(cookie_str)
                my_cookies = {}
                for cookie in cookies:
                    if cookie['name'] == 'goN9uW4i0iKzS' or cookie['name'] == 'goN9uW4i0iKzT':
                        my_cookies[cookie['name']] = cookie['value']
                res, resp = self.getContent(url, method='POST', data=data, cookies=my_cookies)
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
                    self.createDetailPage(url_)
                    self.num = 0
                    kibana_log = f'Detail任务失败'
                    self.logger.warning(kibana_log)
                    # return FetcherStatus.FAIL, '', kibana_log
        except:
            kibana_log = f'Detail任务处理错误，错误原因:{traceback.format_exc()}'
            self.logger.error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log

    def getData(self, task: Task):
        pass

    def createHomePage(self, url, chrome_options=None):
        waitUntilFunc = WebDriverUtil.getDefaultUntilFunc("当前显示")
        WebDriverUtil.closeWebDriver(policyId=self.policyId, driver=self.driver)
        self.driver = WebDriverUtil.openWebDriver(self.policyId, chrome_options)
        self.driver.get(url)
        WebDriverUtil.waitWebDriver(self.driver, waitUntil=waitUntilFunc)
        while True:
            html = self.driver.execute_script("return document.documentElement.outerHTML")
            if '正在加载信息...' in html:
                self.logger.info('正在加载信息...')
                time.sleep(1)
            else:
                break

    def createDetailPage(self, url):
        waitUntilFunc = WebDriverUtil.getDefaultUntilFunc("当前显示")
        WebDriverUtil.closeWebDriver(policyId=self.policyId, driver=self.detail_driver)
        self.detail_driver = WebDriverUtil.openWebDriver(self.policyId)
        self.detail_driver.get(url)
        WebDriverUtil.waitWebDriver(self.detail_driver, waitUntil=waitUntilFunc)
        while True:
            html = self.detail_driver.execute_script("return document.documentElement.outerHTML")
            if '正在加载信息...' in html:
                self.logger.info('正在加载信息...')
                time.sleep(1)
            else:
                break

    def judgeTurnPage(self):
        sleep_time = 0
        while sleep_time <= 10:
            sleep_time += 1
            html = self.driver.execute_script("return document.documentElement.outerHTML")
            if '正在加载信息...' in html:
                self.logger.info('正在加载信息...')
                time.sleep(1)
            else:
                break

    def judgeHomePage(self):
        waitUntilFunc = WebDriverUtil.getDefaultUntilFunc("公告详情")
        WebDriverUtil.waitWebDriver(self.driver, waitUntil=waitUntilFunc)


if __name__ == '__main__':
    policy = Policy(policyId='SBJ',
                    proxy=0,
                    interval=0,
                    duplicate=None,
                    timeout=60,
                    retryTimes=3)
    fetcher = SBJFetcher()
    fetcher.setPolicy(policy=policy)

    urlSign = {
        'url': 'http://yjt.hubei.gov.cn/fbjd/tzgg/index.shtml',
        'pageStart': '1',
        'pageEnd': '2'
    }
    task = Task(taskId=taskId(),
                policyId='SBJ',
                taskType='List',
                urlSign=json.dumps(urlSign, ensure_ascii=False),
                companyName='',
                creditCode=''
                )
    #
    result = fetcher.getList(task)

    if result[0] == FetcherStatus.SUCCESS:
        items = json.loads(result[1])
        for item in items:
            task = Task(taskId=taskId(),
                        policyId='SBJ',
                        taskType='Detail',
                        urlSign=item[0],
                        companyName='',
                        creditCode=''
                        )

            result = fetcher.getDetail(task)
            taskSerialize(task, result)

    #
    urlSign = {
        'url': 'http://wsgg.sbj.cnipa.gov.cn:9080/tmann/annInfoView/annSearch.html?annNum=1805',
        'ann_num': '1768',
        'page_no': '5',
        'ann_type_code': 'TMZCSQ'
    }

    task = Task(taskId=taskId(),
                policyId='SBJ',
                taskType='Detail',
                urlSign=json.dumps(urlSign, ensure_ascii=False),
                companyName='',
                creditCode=''
                )

    result = fetcher.getDetail(task)
    #
    # for i in range(100):
    #     urlSign = {
    #         'url': 'http://wsgg.sbj.cnipa.gov.cn:9080/tmann/annInfoView/annSearch.html?annNum=1805',
    #         'ann_num': '1768',
    #         'page_no': '7',
    #         'ann_type_code': 'TMZCSQ'
    #     }
    #
    #     task = Task(taskId=taskId(),
    #                 policyId='SBJ',
    #                 taskType='Detail',
    #                 urlSign=json.dumps(urlSign, ensure_ascii=False),
    #                 companyName='',
    #                 creditCode=''
    #                 )
    #
    #     result = fetcher.getDetail(task)
