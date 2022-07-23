import json
import random

from framework.core.common_spider.fetcher import NormalFetcher
from framework.core.policy import Policy
from framework.core.task import Task
from framework.utils.fileoperator import taskSerialize

if __name__ == '__main__':
    policyId = 'HENAN_JUNXIAN'
    policy = Policy(policyId=policyId, policyName='测试', taskTypes='List', interval=0.3)
    fetcher = NormalFetcher()
    fetcher.setPolicy(policy)

    companyName = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Content-Type": "application/json"
        },
        "url": "https://www.mohurd.gov.cn/document/search@@q=&t=&c=&on=&odds=&odde=&oc=&tc=&orc=&sc=&bt=2&lt=1&pageSize=30&currentPageNum={pageNums}@@",
        "list": {
            "pageParse": {
                "autoPage": True,
                "pageEnd": 10
            },
            "listParse": {
                "title": {
                    "jsonpath": "$.data.list[*].title"
                },
                "date": {
                    "jsonpath": "$.data.list[*].ofDispatchDate"
                },
                "url": {
                    "jsonpath": "$.data.list[*].url"
                }
            },
            "filterExpre": ""
        },
        "detail": {
            "down": {
                # "main": "*",
                "file": {
                    "xpath": "//a//*[contains(text(),'.doc') or contains(text(),'.pdf') or contains(text(),'.xls') or contains(text(),'.xlsx') or contains(text(),'.rar') or contains(text(),'.zip') or contains(text(),'.xlsx') or contains(text(),'.7z')]/parent::a/@href|//a[contains(text(),'.doc') or contains(text(),'.docx') or contains(text(),'.pdf') or contains(text(),'.xls') or contains(@href,'.doc') or contains(@href,'.pdf') or contains(@href,'.xls') or contains(@href,'.rar') or contains(@href,'.zip') or contains(@href,'.xlsx') or contains(@href,'.7z')]/@href|//img[contains(@src,'/picture')]/@src"
                }
            },
            "filterExpre": ""
        }
    }

    urlSign = {
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
