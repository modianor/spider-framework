import json
import random

from framework.core.common_spider.fetcher import NormalFetcher
from framework.core.policy import Policy
from framework.core.task import Task
from framework.fetcher import FetcherStatus
from framework.utils.fileoperator import taskSerialize

if __name__ == '__main__':
    policyId = 'HENAN_JUNXIAN'
    policy = Policy(policyId=policyId, policyName='测试', taskTypes='List', interval=0.5)
    fetcher = NormalFetcher()
    fetcher.setPolicy(policy)

    companyName = {
        "normal": True,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
        },
        "url": "http://hbj.jiyuan.gov.cn/zcfg/xzcf/index_{pageNums}.html",
        "data": {
            "pageParse": {
                "autoPage": True,
                "diff": 0.995,
                "pageEnd": 3
            },
            "dataParse": {
                "title": {
                    "xpath": "//ul/li/a[contains(text(),'环罚')]/text()"
                },
                "date": {
                    "xpath": "//ul/li/a[contains(text(),'环罚')]/preceding-sibling::span/text()"
                },
                "url": {
                    "xpath": "//ul/li/a[contains(text(),'环罚')]/@href"
                }
            },
            "filterExpre": ""
        }
    }

    print(json.dumps(companyName, ensure_ascii=False))
    urlSign = {
        'url': 'http://hbj.jiyuan.gov.cn/zcfg/xzcf/index.html'
    }

    task = Task(policyId=policyId,
                taskType='Data',
                urlSign=json.dumps(urlSign, ensure_ascii=False),
                companyName=json.dumps(companyName, ensure_ascii=False))
    result = fetcher.getData(task)
    print(result)

    params_json = result[1]
    params = json.loads(params_json)
    for param in params:
        task = Task(
            taskId=random.randint(100000000, 999999999),
            policyId=policyId,
            taskType='Detail',
            urlSign=json.dumps(param, ensure_ascii=False),
            companyName=json.dumps(companyName, ensure_ascii=False)
        )
        result = fetcher.getDetail(task)
        if result[0] == FetcherStatus.SUCCESS:
            taskSerialize(task, result)
