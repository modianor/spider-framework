import time
import traceback
from logging import Logger
from urllib.parse import urlencode

import requests
from requests import Session


class MyRequest(object):
    def __init__(self, session: Session, logger: Logger):
        self.session = None
        self.logger = None
        self.proxies = {}
        self.update(session, logger)

    def update(self, session: Session, logger: Logger):
        self.logger = logger
        self.session: Session = session

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
            response = None
            if curRetryTime < retryTimes + 1:
                try:
                    time.sleep(interval)
                    if params is None or params == {}:
                        self.logger.info(f'使用本地IP 访问GET[{url}] 开始')
                    else:
                        self.logger.info(f'使用本地IP 访问GET[{url + "?" + urlencode(params)}] 开始')
                    if method.upper() == 'GET':
                        if int(proxy) == 0:
                            response = requests.get(url=url, params=params or {}, headers=headers, timeout=timeout,
                                                    **kwargs)
                        elif int(proxy) == 1:
                            proxies = self.getProxy('')
                            response = requests.get(url=url, params=params or {}, headers=headers, timeout=timeout,
                                                    proxies=proxies, **kwargs)

                    elif method.upper() == 'POST':
                        if int(proxy) == 0:
                            response = requests.post(url=url, params=params or {}, data=data, headers=headers,
                                                     timeout=timeout, **kwargs)
                        elif int(proxy) == 1:
                            proxies = self.getProxy('')
                            response = requests.post(url=url, params=params or {}, data=data, headers=headers,
                                                     timeout=timeout, proxies=proxies, **kwargs)

                    statusCode = response.status_code
                    if method.upper() == 'GET':
                        if params is None or params == {}:
                            self.logger.info(f'GET [{url}] status_code:{statusCode}')
                        else:
                            self.logger.info(f'GET [{url + "?" + urlencode(params)}]  status_code:{statusCode}')

                    if curRetryTime + 1 == retryTimes:
                        return False, response

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
                        pass
                except:
                    if curRetryTime + 1 < retryTimes:
                        self.logger.error(f'请求访问错误,即将重试第{curRetryTime + 1}次,错误原因:{traceback.format_exc()}')
                    else:
                        self.logger.error(f'请求访问错误,已重试{curRetryTime + 1}次,放弃治疗,错误原因:{traceback.format_exc()}')

                curRetryTime += 1
            else:
                return False, response

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
