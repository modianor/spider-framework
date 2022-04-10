import json

import requests

from core.task import Task


def insert_list_task():
    for i in range(1, 20):
        urlSign = {'type': '2', 'page_size': '10', 'page': str(i)}
        task = Task(taskId=0,
                    policyId='HEIMAOTOUSU',
                    taskType='List',
                    urlSign=json.dumps(urlSign, sort_keys=True),
                    companyName='',
                    creditCode='',
                    policyMode='plugin'
                    )

        data = {
            'taskParam': json.dumps(task.__dict__, sort_keys=True)
        }
        response = requests.post(url='http://127.0.0.1:6048/task/generateTaskSourceParam', data=data)
        print(response.json())


def insert_data_task():
    for i in range(1, 2):
        urlSign = {'sort_col': '4', 'sort_ord': '2', 'page_size': '10', 'page': str(i)}
        task = Task(taskId=0,
                    policyId='HEIMAOTOUSU',
                    taskType='Data',
                    urlSign=json.dumps(urlSign, sort_keys=True),
                    companyName='',
                    creditCode=''
                    )

        data = {
            'taskParam': json.dumps(task.__dict__, sort_keys=True)
        }
        response = requests.post(url='http://127.0.0.1:6048/task/generateTaskSourceParam', data=data)
        print(response.json())


def insert_normal_task1():
    for i in range(1, 2):
        common_config = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
            },
            "url": "https://www.mee.gov.cn/home/ztbd/rdzl/hjcf/zjcf/index_{pageNums}.shtml",
            "pageParse": {
                "autoPage": True,
                "diff": 0.99,
                "pageStart": 1,
                "pageBegin": 2,
                "pageEnd": 1
            },
            "list": {
                "title": {
                    "xpath": "//ul/li/a[contains(text(),'决定书')]/text()",
                    "replace": {
                        "处.*?书": "****"
                    }
                },
                "date": {"xpath": "//ul/li/a[contains(text(),'决定书')]/preceding-sibling::span/text()"},
                "url": {"xpath": "//ul/li/a[contains(text(),'决定书')]/@href"}
            },
            "detail": {
                "main.html": {},
                "file.*": {}
            },
            "data": {}
        }
        urlSign = {
            "url": "https://www.mee.gov.cn/home/ztbd/rdzl/hjcf/zjcf/index.shtml"
        }

        task = Task(taskId=0, policyId='HENAN_HEBI_JUNXIAN',
                    taskType="List",
                    urlSign=json.dumps(urlSign, ensure_ascii=False),
                    companyName=json.dumps(common_config),
                    policyMode='config')

        data = {
            'taskParam': json.dumps(task.__dict__, sort_keys=True)
        }
        response = requests.post(url='http://127.0.0.1:6048/task/generateTaskSourceParam', data=data)
        print(response.json())


def insert_normal_task2():
    for i in range(1, 2):
        common_config = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
            },
            "url": "http://www.xunxian.gov.cn/xunxian/zfxxgk8659/fdzdgknr1886/hjbh77/dqwrfz/0da41f98-{pageNums}.html",
            "pageParse": {
                "autoPage": True,
                "diff": 0.997
            },
            "list": {
                "title": {
                    "xpath": "//div[@class=\"zfxxgk_zdgkc\"]/ul/li/a[contains(text(),'决定书')]/text()",
                },
                "date": {
                    "xpath": "//div[@class=\"zfxxgk_zdgkc\"]/ul/li/a[contains(text(),'决定书')]/following-sibling::b/text()"},
                "url": {"xpath": "//div[@class=\"zfxxgk_zdgkc\"]/ul/li/a[contains(text(),'决定书')]/@href"}
            },
            "detail": {
                "main.html": {},
                "file.*": {}
            },
            "data": {}
        }
        urlSign = {}

        task = Task(taskId=0, policyId='HENAN_HEBI_JUNXIAN',
                    taskType="List",
                    urlSign=json.dumps(urlSign, ensure_ascii=False),
                    companyName=json.dumps(common_config),
                    policyMode='config')
        data = {
            'taskParam': json.dumps(task.__dict__, sort_keys=True)
        }
        response = requests.post(url='http://127.0.0.1:6048/task/generateTaskSourceParam', data=data)
        print(response.json())


def insert_normal_data_task():
    common_config = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
        },
        "url": "http://hbj.jiyuan.gov.cn/zcfg/xzcf/index_{pageNums}.html",
        "pageParse": {
            "autoPage": True,
            "diff": 0.995,
            "pageStart": 1,
            "pageBegin": 2,
            "pageEnd": 100
        },
        "data": {
            "title": {
                "xpath": "//ul/li/a[contains(text(),'济环罚决字')]/text()"
            },
            "date": {"xpath": "//ul/li/a[contains(text(),'济环罚决字')]/preceding-sibling::span/text()"},
            "url": {"xpath": "//ul/li/a[contains(text(),'济环罚决字')]/@href"}
        }
    }
    urlSign = {
        "url": "http://hbj.jiyuan.gov.cn/zcfg/xzcf/index.html"
    }

    task = Task(taskId=0, policyId='HENAN_HEBI_JUNXIAN',
                taskType="Data",
                urlSign=json.dumps(urlSign, ensure_ascii=False),
                companyName=json.dumps(common_config),
                policyMode='config')
    data = {
        'taskParam': json.dumps(task.__dict__, sort_keys=True)
    }
    response = requests.post(url='http://127.0.0.1:6048/task/generateTaskSourceParam', data=data)
    print(response.json())


insert_normal_data_task()
