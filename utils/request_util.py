import time
from logging import Logger
from urllib.parse import urlencode

import requests
from requests import Session

from utils.single import Singleton


@Singleton
class MyRequest(object):
    def __init__(self, session: Session, logger: Logger):
        self.logger = logger
        self.session: Session = session
        self.proxies = {}

    def getContent(self, url,
                   method='GET',
                   params=None,
                   headers=None,
                   data=None,
                   timeout=60,
                   retryTimes=3,
                   interval=3,
                   proxy=0,
                   validFunc=None,
                   **kwargs):
        curRetryTime = 0
        while True:
            if curRetryTime < retryTimes:
                response = None
                time.sleep(interval)
                if params is None or params == {}:
                    self.logger.info(f'使用本地IP 访问GET[{url}]')
                else:
                    self.logger.info(f'使用本地IP 访问GET[{url + "?" + urlencode(params)}]')
                if method.upper() == 'GET':
                    if proxy == 0:
                        response = requests.get(url=url, params=params or {}, headers=headers, timeout=timeout,
                                                **kwargs)
                    elif proxy == 1:
                        proxies = self.getProxy('')
                        response = requests.get(url=url, params=params or {}, headers=headers, timeout=timeout,
                                                proxies=proxies, **kwargs)

                elif method.upper() == 'POST':
                    if proxy == 0:
                        response = requests.post(url=url, params=params or {}, data=data, headers=headers,
                                                 timeout=timeout, **kwargs)
                    elif proxy == 1:
                        proxies = self.getProxy('')
                        response = requests.post(url=url, params=params or {}, data=data, headers=headers,
                                                 timeout=timeout, proxies=proxies, **kwargs)

                statusCode = response.status_code
                if statusCode == 200:
                    if validFunc:
                        validStatus = validFunc(response)
                        if validStatus:
                            return True, response
                        else:
                            self.logger.warning('请求结果未通过自定义函数校验')
                            return False, response
                    else:
                        return True, response
                else:
                    if curRetryTime + 1 == retryTimes:
                        return False, response

                curRetryTime += 1
            else:
                break

    def getProxy(self, policyId):
        # url = f'http://modianor.proxy/getProxy?policyId={policyId}'
        # r = requests.get(url)
        proxies = {
            'http': '127.0.0.1:8888',
            'https': '127.0.0.1:8888'
        }
        self.logger.info(f'获取代理IP: {str(proxies)}')
        return proxies



if __name__ == '__main__':
    session = Session()
    myReq: MyRequest = MyRequest(session=session)
    res, resp = myReq.getContent(url='http://www.baidu.com',
                                 method='GET',
                                 interval=1,
                                 proxy=1
                                 )
    print(res, resp)
