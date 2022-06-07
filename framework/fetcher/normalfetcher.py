import json
import re
import traceback
from datetime import datetime
from typing import Dict
from urllib.parse import urljoin

import Levenshtein
from lxml import etree
from lxml.etree import _Element
from requests import Session

from framework.core.task import Task
from framework.fetcher import Fetcher, FetcherStatus
from framework.utils.log import Logger
from framework.utils.params import getPolicy
from framework.utils.request_util import MyRequest


class NormalFetcher(Fetcher):

    def __init__(self) -> None:
        super().__init__()
        self.policyId = 'NORMAL'
        self.logger = Logger(self.policyId.lower()).getlog()
        self.session: Session = Session()
        self.myRequest: MyRequest = MyRequest(self.session, self.logger)
        self.policy = None

    def fieldReplace(self, values, rules: Dict[str, str]):
        if not values:
            return values
        if isinstance(values, list):
            li = []
            for value in values:
                for k, v in rules.items():
                    li.append(re.sub(k, v, str(value)))
            return li

        if isinstance(values, str):
            res = ''
            for k, v in rules.items():
                res = re.sub(k, v, values)
            return res

    def parseFieldByRule(self, content, rules):

        if 'xpath' in rules.keys():
            try:
                rule = rules['xpath']
                tree: _Element = etree.HTML(content)
                values = tree.xpath(rule)
                if 'replace' in rules.keys():
                    values = self.fieldReplace(values, rules.get('replace', {}))
                return values
            except:
                return None
        elif 'regex' in rules.keys():
            try:
                rule = rules['regex']
                values = re.findall(rule, content)
                if 'replace' in rules.keys():
                    values = self.fieldReplace(values, rules.get('replace', {}))
                return values
            except:
                return None
        elif 'jsonpath' in rules.keys():
            pass
        elif 'css' in rules.keys():
            pass

    def parseText(self, context):
        pass

    def parseList(self, context, html):
        config = context.get('config')
        if 'list' in config:
            listParseConfig = config.get('list', {})
            data = dict()
            dataLen = 0
            for field in listParseConfig:
                fieldParseRules = listParseConfig[field]
                values = self.parseFieldByRule(html, fieldParseRules)
                data[field] = values
                self.logger.info(f'解析[{field}]:{len(values)}')
                if field == 'url':
                    dataLen = len(values)
                    for i in range(dataLen):
                        values[i] = urljoin(context['url'], values[i])

            for field in data:
                fieldValues = data[field]
                for i in range(dataLen):
                    pass

            # 这里需要检查解析出来的每个字段的个数
            infos = list()
            for i in range(dataLen):
                info = dict()
                for field in data:
                    info[field] = str(data[field][i])
                infos.append(info)
            return infos

    def parseData(self, context, html):
        config = context.get('config')
        if 'data' in config:
            listParseConfig = config.get('data', {})
            data = dict()
            dataLen = 0
            for field in listParseConfig:
                fieldParseRules = listParseConfig[field]
                values = self.parseFieldByRule(html, fieldParseRules)
                data[field] = values
                self.logger.info(f'解析[{field}]:{len(values)}')
                if field == 'url':
                    dataLen = len(values)
                    for i in range(dataLen):
                        values[i] = urljoin(context['url'], values[i])

            for field in data:
                fieldValues = data[field]
                for i in range(dataLen):
                    pass

            # 这里需要检查解析出来的每个字段的个数
            infos = list()
            for i in range(dataLen):
                info = dict()
                for field in data:
                    info[field] = str(data[field][i])
                infos.append(info)
            return infos

    def turnListPage(self, context):
        urlList = []
        preHtml = ''
        config = context.get('config', {})
        headers = config.get("headers", {})
        # 翻页解析配置
        pageParseConfig = config.get("pageParse", {})
        # 翻页起始页第一页
        pageStart = pageParseConfig.get("pageStart", 1)
        # 翻页起始页第二页
        pageBegin = pageParseConfig.get("pageBegin", 2)
        # 总页码解析配置
        pageNums = pageParseConfig.get("pageNums", {})
        # 指定结束页码
        pageEnd = pageParseConfig.get("pageEnd", 200)
        # 当前页与前一页文本相似度
        sameDiff = pageParseConfig.get("diff", 0.99)
        # 当前访问的url地址
        # url = context.get('url')
        # 任务参数列表
        urlSign = context['urlSign']
        # 翻页url模板
        urlTemp = context.get('urlTemp')
        # List任务生成Detail任务的参数
        context["listParams"] = []
        policyId = context.get('policyId')
        try:

            url = urlSign.get('url', '')
            if url == '':
                pass
                # url为空的情况下 此时url直接使用pageStart和pageBegin拼装
            else:
                # url不为空的情况 需要先解析任务传递的url页面 然后再使用pageStart和pageBegin拼装
                context['url'] = url
                res, response = self.getContent(url, headers=headers, method='GET')
                response.encoding = 'utf-8'
                html = response.text
                # 解析任务传递的url页面
                infos = self.parseList(context, html)
                curListParams = []
                for info in infos:
                    curListParams.append([info, '', '', f'{policyId}|Detail'])
                self.logger.info(f'ListParse解析当前页【{context["url"]}】得到{len(infos)}个listParams')
                context['listParams'] = context['listParams'] + curListParams

            # url直接使用pageStart和pageBegin拼装
            param_maps = {"pageNums": pageStart}
            param_maps.update(urlSign)
            url = urlTemp.format_map(param_maps)

            res, response = self.getContent(url, headers=headers, method='GET')
            response.encoding = 'utf-8'
            preHtml = response.text
            preUrl = url
            context['url'] = preUrl

            if "autoPage" in pageParseConfig and pageParseConfig["autoPage"]:
                # 自动翻页
                for i in range(pageBegin, 10000000000):
                    param_maps = {"pageNums": i}
                    param_maps.update(urlSign)
                    curUrl = urlTemp.format_map(param_maps)
                    res, response = self.getContent(curUrl, headers=headers, method='GET')
                    response.encoding = 'utf-8'
                    curHtml = response.text
                    threshold = Levenshtein.ratio(preHtml, curHtml)
                    if threshold > sameDiff:
                        # 相似度超过阈值 出现重复了
                        self.logger.warning(f'第{i}页与第{i - 1}页相似度：{threshold},超过指定阈值{sameDiff},停止自动翻页')
                        break
                    else:
                        context['url'] = preUrl
                        # 这里做解析保存处理
                        infos = self.parseList(context, preHtml)
                        # 继续翻页
                        curListParams = []
                        for info in infos:
                            curListParams.append([info, '', '', f'{policyId}|Detail'])
                        self.logger.info(f'ListParse解析当前页【{context["url"]}】得到{len(infos)}个listParams')
                        context['listParams'] = context['listParams'] + curListParams
                        preHtml = curHtml
                        preUrl = curUrl
                    # 超过指定结束页码
                    if i > pageEnd:
                        break
                # 请求访问 比较和前一个页面的相似度
                # 如果相似度超过阈值 则自动翻页结束
                # 如果相似度没有超过阈值，则继续翻页
            else:
                # 手动解析
                if "pageNums" in pageParseConfig:
                    # 手动指定或者规则化抽取
                    pageNumsConfig = pageParseConfig['pageNums']
                    values = self.parseFieldByRule(preHtml, pageNumsConfig)
                    if values and len(values) > 0:
                        pageNums = int(values[0])
                    self.logger.info(f'TextParse解析当前页【{context["url"]}】解析pageNums: {pageNums}')
                    param_maps = {"pageNums": pageStart}
                    param_maps.update(urlSign)
                    mainUrl = url.format_map(param_maps)
                    urlList.append(mainUrl)
                    for i in range(pageBegin, pageNums + 1):
                        if i > pageEnd:
                            break
                        param_maps = {"pageNums": i}
                        param_maps.update(urlSign)
                        mainUrl = urlTemp.format_map(param_maps)
                        urlList.append(mainUrl)

                    for curUrl in urlList:
                        res, response = self.getContent(curUrl, headers=headers, method='GET')
                        response.encoding = 'utf-8'
                        curHtml = response.text
                        context['url'] = curUrl
                        infos = self.parseList(context, curHtml)
                        curListParams = []
                        for info in infos:
                            curListParams.append([info, '', '', f'{policyId}|Detail'])
                        self.logger.info(f'ListParse解析当前页【{context["url"]}】得到{len(infos)}个listParams')
                        context['listParams'] = context['listParams'] + curListParams
            kibana_log = f'List任务成功, 生成{len(context["listParams"])}个Detail任务'
            self.logger.info(kibana_log)
            return FetcherStatus.SUCCESS, json.dumps(context["listParams"], ensure_ascii=False,
                                                     sort_keys=True), kibana_log
        except:
            kibana_log = f'List任务处理错误，错误原因:{traceback.format_exc()}'
            self.logger.error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log

    def turnDataPage(self, context):
        urlList = []
        preHtml = ''
        config = context.get('config', {})
        headers = config.get("headers", {})
        # 翻页解析配置
        pageParseConfig = config.get("pageParse", {})
        # 翻页起始页第一页
        pageStart = pageParseConfig.get("pageStart", 1)
        # 翻页起始页第二页
        pageBegin = pageParseConfig.get("pageBegin", 2)
        # 总页码解析配置
        pageNums = pageParseConfig.get("pageNums", {})
        # 指定结束页码
        pageEnd = pageParseConfig.get("pageEnd", 200)
        # 当前页与前一页文本相似度
        sameDiff = pageParseConfig.get("diff", 0.99)
        # 当前访问的url地址
        # url = context.get('url')
        # 任务参数列表
        urlSign = context['urlSign']
        # 翻页url模板
        urlTemp = context.get('urlTemp')
        # List任务生成Detail任务的参数
        context["dataParams"] = []
        policyId = context.get('policyId')
        try:

            url = urlSign.get('url', '')
            if url == '':
                pass
                # url为空的情况下 此时url直接使用pageStart和pageBegin拼装
            else:
                # url不为空的情况 需要先解析任务传递的url页面 然后再使用pageStart和pageBegin拼装
                context['url'] = url
                res, response = self.getContent(url, headers=headers, method='GET')
                response.encoding = 'utf-8'
                html = response.text
                # 解析任务传递的url页面
                infos = self.parseData(context, html)
                self.logger.info(f'DataParse解析当前页【{context["url"]}】得到{len(infos)}个dataParams')
                context['dataParams'] = context['dataParams'] + infos

            # url直接使用pageStart和pageBegin拼装
            param_maps = {"pageNums": pageStart}
            param_maps.update(urlSign)
            url = urlTemp.format_map(param_maps)

            res, response = self.getContent(url, headers=headers, method='GET')
            response.encoding = 'utf-8'
            preHtml = response.text
            preUrl = url
            context['url'] = preUrl

            if "autoPage" in pageParseConfig and pageParseConfig["autoPage"]:
                # 自动翻页
                for i in range(pageBegin, 10000000000):
                    param_maps = {"pageNums": i}
                    param_maps.update(urlSign)
                    curUrl = urlTemp.format_map(param_maps)
                    res, response = self.getContent(curUrl, headers=headers, method='GET')
                    response.encoding = 'utf-8'
                    curHtml = response.text
                    threshold = Levenshtein.ratio(preHtml, curHtml)
                    if threshold > sameDiff:
                        # 相似度超过阈值 出现重复了
                        self.logger.warning(f'第{i}页与第{i - 1}页相似度：{threshold},超过指定阈值{sameDiff},停止自动翻页')
                        break
                    else:
                        context['url'] = preUrl
                        # 这里做解析保存处理
                        infos = self.parseData(context, preHtml)
                        self.logger.info(f'DataParse解析当前页【{context["url"]}】得到{len(infos)}个dataParams')
                        context['dataParams'] = context['dataParams'] + infos
                        # 继续翻页
                        preHtml = curHtml
                        preUrl = curUrl
                    # 超过指定结束页码
                    if i > pageEnd:
                        break
                # 请求访问 比较和前一个页面的相似度
                # 如果相似度超过阈值 则自动翻页结束
                # 如果相似度没有超过阈值，则继续翻页
            else:
                # 手动解析
                if "pageNums" in pageParseConfig:
                    # 手动指定或者规则化抽取
                    pageNumsConfig = pageParseConfig['pageNums']
                    values = self.parseFieldByRule(preHtml, pageNumsConfig)
                    if values and len(values) > 0:
                        pageNums = int(values[0])
                    self.logger.info(f'TextParse解析当前页【{context["url"]}】解析pageNums: {pageNums}')
                    param_maps = {"pageNums": pageStart}
                    param_maps.update(urlSign)
                    mainUrl = url.format_map(param_maps)
                    urlList.append(mainUrl)
                    for i in range(pageBegin, pageNums + 1):
                        if i > pageEnd:
                            break
                        param_maps = {"pageNums": i}
                        param_maps.update(urlSign)
                        mainUrl = urlTemp.format_map(param_maps)
                        urlList.append(mainUrl)

                    for curUrl in urlList:
                        res, response = self.getContent(curUrl, headers=headers, method='GET')
                        response.encoding = 'utf-8'
                        curHtml = response.text
                        context['url'] = curUrl
                        infos = self.parseData(context, curHtml)
                        self.logger.info(f'DataParse解析当前页【{context["url"]}】得到{len(infos)}个dataParams')
                        context['dataParams'] = context['dataParams'] + infos
            kibana_log = f'Data任务成功, 生成{len(context["dataParams"])}个Data任务'
            self.logger.info(kibana_log)
            return FetcherStatus.SUCCESS, json.dumps(context["dataParams"], ensure_ascii=False,
                                                     sort_keys=True), kibana_log
        except:
            kibana_log = f'List任务处理错误，错误原因:{traceback.format_exc()}'
            self.logger.error(kibana_log)
            return FetcherStatus.FAIL, '', kibana_log

    def updatePolicy(self, task: Task):
        policys = getPolicy([task.policyId])
        for policy in policys:
            self.logger = Logger(task.policyId.lower()).getlog()
            self.myRequest.update(self.session, self.logger)
            self.setPolicy(policy=policy)

    def getDetail(self, task: Task):
        try:
            self.updatePolicy(task)
            self.logger.info(f'通用配置爬虫正在处理 policyId:{task.policyId}, Detail任务参数:{task.urlSign}')
            context = {}
            policyId = task.policyId
            urlSign = task.urlSign
            commonConfig = task.companyName

            context['policyId'] = policyId
            context['urlSign'] = urlSign
            context['config'] = commonConfig

            url = urlSign['url']
            content = list()

            res, resp = self.getContent(url, method='GET')
            if res:
                resp.encoding = 'utf-8'
                content.append({'index.html': resp.text})
                info = {
                    'policyId': task.policyId,
                    'taskId': task.taskId,
                    'url': url,
                    'downloadUrl': url,
                    'downloadTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                info.update(urlSign)
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

    def getList(self, task: Task):
        self.updatePolicy(task)
        self.logger.info(f'通用配置爬虫正在处理 policyId:{task.policyId}, List任务参数:{task.urlSign}')
        # 上下文容器
        context = {}
        policyId = task.policyId
        urlSign = task.urlSign
        commonConfig = task.companyName
        urlTemp = commonConfig.get("url", "")

        context['policyId'] = policyId
        context['urlSign'] = urlSign
        context['config'] = commonConfig
        context['urlTemp'] = urlTemp
        result = self.turnListPage(context)
        return result

    def getData(self, task: Task):
        self.updatePolicy(task)
        self.logger.info(f'通用配置爬虫正在处理 policyId:{task.policyId}, Data任务参数:{task.urlSign}')
        # 上下文容器
        context = {}
        policyId = task.policyId
        urlSign = task.urlSign
        commonConfig = task.companyName
        urlTemp = commonConfig.get("url", "")

        context['policyId'] = policyId
        context['urlSign'] = urlSign
        context['config'] = commonConfig
        context['urlTemp'] = urlTemp
        result = self.turnDataPage(context)
        return result
