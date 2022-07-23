import json
import random

from framework.core.common_spider.fetcher import NormalFetcher
from framework.core.policy import Policy
from framework.core.task import Task
from framework.utils.fileoperator import taskSerialize

if __name__ == '__main__':
    policyId = 'HENAN_JUNXIAN'
    policy = Policy(policyId=policyId, policyName='测试', taskTypes='List', interval=.5)
    fetcher = NormalFetcher()
    fetcher.setPolicy(policy)

    companyName = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
        },
        "url": "http://hbj.jiyuan.gov.cn/zcfg/xzcf/index_{pageNums*2}.html?start={pageNums*2+1000000}&end=start={pageNums*2+3000000}",
        "list": {
            "pageParse": {
                "autoPage": True,
                "diff": 0.995,
                "pageStart": 1,
                "pageBegin": 2,
                "pageEnd": 4
            },
            "listParse": {
                "title": {
                    "xpath": "//ul/li/a[contains(text(),'济环罚决字')]/text()"
                },
                "date": {
                    "xpath": "//ul/li/a[contains(text(),'济环罚决字')]/preceding-sibling::span/text()"
                },
                "url": {
                    "xpath": "//ul/li/a[contains(text(),'济环罚决字')]/@href"
                }
            },
            "filterExpre": "'河南省' not in title and date == '2021-11-03'"
        },
        "detail": {
            "down": {

            },
            "filterExpre": ""
        }
    }

    urlSign = {}

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
