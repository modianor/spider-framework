import json
import random

from framework.core.common_spider.fetcher import NormalFetcher
from framework.core.policy import Policy
from framework.core.task import Task
from framework.utils.fileoperator import taskSerialize

if __name__ == '__main__':
    policyId = 'HENAN_JUNXIAN'
    policy = Policy(policyId=policyId, policyName='测试', taskTypes='List', interval=1)
    fetcher = NormalFetcher()
    fetcher.setPolicy(policy)

    companyName = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
            # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Content-Type": "application/json"
        },
        "url": "http://www.hbfcx.gov.cn/module/web/jpage/dataproxy.jsp?startrecord={(pageNums-1)*15+1}&endrecord={pageNums*15}&perpage=15@@col=1&appid=1&webid=12&path=%2F&columnid=782&sourceContentType=1&unitid=3644&webname=%E9%98%9C%E5%9F%8E%E5%8E%BF%2C%E9%98%9C%E5%9F%8E%E5%8E%BF%E4%BA%BA%E6%B0%91%E6%94%BF%E5%BA%9C&permissiontype=0&testNum={pageNums * 10}@@",
        "list": {
            "pageParse": {
                "pageNums": 4
            },
            "listParse": {
                "title": {
                    "regex": "title='(.*?)'"
                },
                "date": {
                    "regex": "<span>\\[(\\d+-\\d+-\\d+)\\]</span>"
                },
                "url": {
                    "regex": "href='(.*?art.*?)'"
                }
            },
            "filterExpre": ""
        },
        "detail": {
            "down": {
                # "main": "*",
                "pic": {
                    "xpath": "//a//*[contains(text(),'.doc') or contains(text(),'.pdf') or contains(text(),'.xls') or contains(text(),'.xlsx') or contains(text(),'.rar') or contains(text(),'.zip') or contains(text(),'.xlsx') or contains(text(),'.7z')]/parent::a/@href|//a[contains(text(),'.doc') or contains(text(),'.docx') or contains(text(),'.pdf') or contains(text(),'.xls') or contains(@href,'.doc') or contains(@href,'.pdf') or contains(@href,'.xls') or contains(@href,'.rar') or contains(@href,'.zip') or contains(@href,'.xlsx') or contains(@href,'.7z')]/@href|//img[contains(@src,'/picture')]/@src"
                }
            },
            "filterExpre": ""
        }
    }

    urlSign = {
        "url": "http://www.hbfcx.gov.cn/col/col782/index.html?uid=3644&pageNum=1"
    }

    task = Task(policyId=policyId,
                taskType='List',
                urlSign=json.dumps(urlSign, ensure_ascii=False),
                companyName=json.dumps(companyName, ensure_ascii=False))
    result = fetcher.getList(task)
    print(result)

    params_json = result[1]
    params = json.loads(params_json)
    for param in params:
        task = Task(
            taskId=random.randint(100000000, 999999999),
            policyId=policyId,
            taskType='Detail',
            urlSign=param[0],
            companyName=json.dumps(companyName, ensure_ascii=False)
        )
        result = fetcher.getDetail(task)
        taskSerialize(task, result)
