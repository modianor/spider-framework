import re
import traceback
from typing import Dict

import Levenshtein
from lxml import etree

from framework.core.common_spider.page_download import PageDownloader
from framework.core.common_spider.text_parse import FieldParser
from framework.utils.log import Logger


class PageTurner:

    def __init__(self, getContent) -> None:
        super().__init__()
        self.getContent = getContent

    def parsePage(self, context, html, configType='list'):
        """
        根据请求响应解析字段
        Args:
            context: 上下文信息
            html: 响应信息
            configType: 解析配置的任务类型

        Returns: [{k1:v1},{},{}]
        """
        fieldParser = FieldParser()
        data = fieldParser.field_parse(context, html, configType)
        data = fieldParser.item_fill_up(context, data)
        result = fieldParser.item_reduce(context, data)
        return result

    def getCurrentLogger(self, policyId='normal'):
        return Logger(policyId).getlog()

    @staticmethod
    def dynamicCalcStr(urlTemplate, data):
        expres = re.findall('(\\{.*?\\})', urlTemplate)
        for expre in expres:
            expre_value = eval(expre[1:-1], data)
            urlTemplate = urlTemplate.replace(expre, str(expre_value))
        return urlTemplate

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
            # xpath语法解析
            try:
                rule = rules['xpath']
                tree = etree.HTML(content)
                values = tree.xpath(rule)
                if 'replace' in rules.keys():
                    values = self.fieldReplace(values, rules.get('replace', {}))
                return values
            except:
                return []
        elif 'regex' in rules.keys():
            # regex语法解析
            try:
                rule = rules['regex']
                values = re.findall(rule, content)
                if 'replace' in rules.keys():
                    values = self.fieldReplace(values, rules.get('replace', {}))
                return values
            except:
                return []
        elif 'jsonpath' in rules.keys():
            # jsonp语法解析
            pass
        elif 'css' in rules.keys():
            # css定位语法解析
            pass

    def turnPage(self, context, configType='list'):
        urlList = []
        preHtml = ''
        # 爬虫任务业务配置
        config = context.get('config', {})
        # 全局请求header
        headers = config.get("headers", {})
        # 全局请求encoding
        encoding = config.get("encoding", 'utf-8')
        # list任务配置
        listConfig = config.get(configType, {})
        # 翻页解析配置
        pageParseConfig = listConfig.get("pageParse", {})
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
        urlTemplate = context.get('urlTemplate')
        # List任务生成Detail任务的参数
        context["Params"] = []
        # 当前任务所属的策略ID
        policyId = context.get('policyId')
        try:
            url = urlSign.get('url', '')
            if url != '':
                # url不为空的情况 需要先解析任务传递的url页面 然后再使用pageStart和pageBegin拼装
                context['url'] = url
                res, response = self.getContent(url, headers=headers, method='GET')
                response.encoding = encoding
                html = response.text
                # 解析任务传递的url页面
                curParams = self.parsePage(context, html, configType=configType)
                self.getCurrentLogger(policyId.lower()).info(
                    f'{configType}Parse解析当前页【{context["url"]}】得到{len(curParams)}个{configType}Params')
                context['Params'] = context['Params'] + curParams

            # url直接使用pageStart和pageBegin拼装
            param_maps = {"pageNums": pageStart}
            param_maps.update(urlSign)
            # url = urlTemplate.format_map(param_maps)
            url = self.dynamicCalcStr(urlTemplate, param_maps)
            res, response = PageDownloader.downloadFile(self.getContent, url, context)
            response.encoding = 'utf-8'
            preHtml = response.text
            preUrl = url
            context['url'] = preUrl

            if "autoPage" in pageParseConfig and pageParseConfig["autoPage"]:
                # 自动翻页
                for i in range(pageBegin, 10000000000):
                    param_maps = {"pageNums": i}
                    param_maps.update(urlSign)
                    # curUrl = urlTemplate.format_map(param_maps)
                    curUrl = self.dynamicCalcStr(urlTemplate, param_maps)
                    res, response = PageDownloader.downloadFile(self.getContent, curUrl, context)
                    response.encoding = 'utf-8'
                    curHtml = response.text
                    threshold = Levenshtein.ratio(preHtml, curHtml)
                    if threshold > sameDiff:
                        # 相似度超过阈值 出现重复了
                        self.getCurrentLogger(policyId.lower()).warning(
                            f'第{i}页与第{i - 1}页相似度：{threshold},超过指定阈值{sameDiff},停止自动翻页')
                        break
                    else:
                        self.getCurrentLogger(policyId.lower()).info(
                            f'第{i}页与第{i - 1}页相似度：{threshold},继续自动翻页')
                        context['url'] = preUrl
                        # 这里做解析保存处理
                        curParams = self.parsePage(context, preHtml, configType=configType)
                        # 继续翻页
                        self.getCurrentLogger(policyId.lower()).info(
                            f'{configType}Parse解析当前页【{context["url"]}】得到{len(curParams)}个{configType}Params')
                        context['Params'] = context['Params'] + curParams
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
                    if isinstance(pageNumsConfig, int):
                        pageNums = pageNumsConfig
                    else:
                        values = self.parseFieldByRule(preHtml, pageNumsConfig)
                        if values and len(values) > 0:
                            pageNums = int(values[0])
                    self.getCurrentLogger(policyId.lower()).info(
                        f'TextParse解析当前页【{context["url"]}】解析pageNums: {pageNums}')
                    param_maps = {"pageNums": pageStart}
                    param_maps.update(urlSign)
                    mainUrl = self.dynamicCalcStr(urlTemplate, param_maps)
                    urlList.append(mainUrl)
                    for i in range(pageBegin, pageNums + 1):
                        if i > pageEnd:
                            break
                        param_maps = {"pageNums": i}
                        param_maps.update(urlSign)
                        mainUrl = self.dynamicCalcStr(urlTemplate, param_maps)
                        urlList.append(mainUrl)

                    for curUrl in urlList:
                        res, response = PageDownloader.downloadFile(self.getContent, url, context)
                        response.encoding = 'utf-8'
                        curHtml = response.text
                        context['url'] = curUrl
                        curParams = self.parsePage(context, curHtml, configType=configType)
                        self.getCurrentLogger(policyId.lower()).info(
                            f'{configType}Parse解析当前页【{context["url"]}】得到{len(curParams)}个{configType}Params')
                        context['Params'] = context['Params'] + curParams
            return context["Params"]
        except:
            kibana_log = f'List任务处理错误，错误原因:{traceback.format_exc()}'
            self.getCurrentLogger(policyId.lower()).error(kibana_log)
            return []
