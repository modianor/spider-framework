import json
import re
from typing import Dict
from urllib.parse import urljoin

from jsonpath import jsonpath
from lxml import etree


class FieldParser:
    def __init__(self) -> None:
        super().__init__()

    def get_item_len(self, items):
        param_lists = list(items.values())

        if len(param_lists) == 0:
            return 0

        init_len = len(param_lists[0])

        for single_params in param_lists:
            if len(single_params) != init_len:
                return 0

        return init_len

    def item_filter(self, context, param_map_lists):
        result_list = []
        config = context.get('config', {})
        listConfig = config.get('list', {})
        filterExpre = listConfig.get('filterExpre', "")

        if filterExpre.count(" ") == len(filterExpre):
            return param_map_lists

        for param_map in param_map_lists:
            if eval(filterExpre, param_map):
                param_map.popitem()
                result_list.append(param_map)
        return result_list

    def item_reduce(self, context, items):
        single_params_len = self.get_item_len(items)
        param_map_lists = []
        for i in range(single_params_len):
            single_param_map = {}
            for item_params in items:
                single_param_map[item_params] = items[item_params][i]
            param_map_lists.append(single_param_map)
        param_map_lists = self.item_filter(context, param_map_lists)
        return param_map_lists

    def fill_up(self, wait_fill_up_value, param_map_list):
        filled_values = []
        for param_map in param_map_list:
            filled_value = wait_fill_up_value.format_map(param_map)
            filled_values.append(filled_value)
        return filled_values

    def split_items(self, items):
        wait_fill_up_items = {}
        pure_items = {}
        for field in items:
            value = items[field]
            if isinstance(value, str):
                wait_fill_up_items[field] = value
            elif isinstance(value, list):
                pure_items[field] = value
            else:
                raise Exception('存在不可处理类型的item')
        return wait_fill_up_items, pure_items

    def item_fill_up(self, context, items):
        wait_fill_up_items, pure_items = self.split_items(items)
        param_map_lists = self.item_reduce(context, pure_items)

        for wait_fill_up_item_key in wait_fill_up_items:
            value = wait_fill_up_items[wait_fill_up_item_key]
            filled_values = self.fill_up(value, param_map_lists)
            pure_items[wait_fill_up_item_key] = filled_values

        if 'url' in pure_items:
            urls = pure_items['url']
            pure_items['url'] = self.url_fix(urls, context)
        return pure_items

    @staticmethod
    def url_fix(urls, context):
        curUrl = context.get('url', '')
        for i in range(len(urls)):
            urls[i] = urljoin(curUrl, urls[i])
        return urls

    def field_parse(self, context, html, configType='list'):
        data = dict()
        config = context.get('config')
        if configType in config:
            listConfig = config.get(configType, {})
            listParseConfig = listConfig.get(f'{configType}Parse', {})
            for field in listParseConfig:
                # 每个字段解析的规则
                fieldParseRules = listParseConfig[field]
                if isinstance(fieldParseRules, dict):
                    # 需要直接从html种解析
                    values = self.parseFieldByRule(html, fieldParseRules)
                    data[field] = values
                elif isinstance(fieldParseRules, str):
                    # 需要若干个解析好的字段进行拼接
                    data[field] = fieldParseRules
        return data

    @staticmethod
    def fieldReplace(values, rules: Dict[str, str]):
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

    @staticmethod
    def transferElementToStr(values):
        result = []
        for value in values:
            result.append(str(value))
        return result

    @staticmethod
    def parseFieldByRule(content, rules):
        if 'xpath' in rules.keys():
            # xpath语法解析
            try:
                rule = rules['xpath']
                tree = etree.HTML(content)
                values = tree.xpath(rule)
                values = FieldParser.transferElementToStr(values)
                if 'replace' in rules.keys():
                    values = FieldParser.fieldReplace(values, rules.get('replace', {}))
                return values
            except:
                return []
        elif 'regex' in rules.keys():
            # regex语法解析
            try:
                rule = rules['regex']
                values = re.findall(rule, content)
                if 'replace' in rules.keys():
                    values = FieldParser.fieldReplace(values, rules.get('replace', {}))
                return values
            except:
                return []
        elif 'jsonpath' in rules.keys():
            # jsonp语法解析
            try:
                rule = rules['jsonpath']
                json_data = json.loads(content)
                values = jsonpath(json_data, rule)
                if 'replace' in rules.keys():
                    values = FieldParser.fieldReplace(values, rules.get('replace', {}))
                return values
            except:
                return []
        elif 'css' in rules.keys():
            # css定位语法解析
            pass
