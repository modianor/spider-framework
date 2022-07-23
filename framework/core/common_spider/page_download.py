import json
import os
import re
from urllib.parse import parse_qs

from framework.core.common_spider.text_parse import FieldParser
from framework.utils.fileoperator import createTaskHome, TaskHomeExist, getTaskHomePath

url_sign = ['doc', 'docx', 'pdf', 'xls', 'xlsx', 'rar', 'prn', 'dot', 'wbk', 'rtf', 'txt', 'png', 'jpg',
            'jpeg', 'gif', 'bmp', 'zip', 'wps', 'et', 'tif', 'tiff', 'swf']


class PageDownloader:
    @staticmethod
    def dynamicCalcStr(urlTemplate, data):
        expres = re.findall('(\\{.*?\\})', urlTemplate)
        for expre in expres:
            expre_value = eval(expre[1:-1], data)
            data.popitem()
            urlTemplate = urlTemplate.replace(expre, str(expre_value))
        return urlTemplate

    @staticmethod
    def detectFileType(url, response):
        try:
            if response.headers.get('Content-Type') and 'text/html' in response.headers['Content-Type']:
                suffix = 'html'
                return suffix
            elif response.headers.get('Content-Type') and 'application/vnd.ms-excel' in response.headers[
                'Content-Type']:
                suffix = 'xls'
                return suffix
            else:
                for key in url_sign:
                    if response.headers.get('content-disposition') and '.' + key in response.headers[
                        'content-disposition']:
                        suffix = key
                        return suffix
                    elif response.headers.get('Content-Type') and key in response.headers['Content-Type']:
                        suffix = key
                        return suffix

            dot_index = url.rfind('.')
            if dot_index > 0:
                extension = url[dot_index + 1:]
                if extension:
                    suffix = extension.lower()
                    if suffix in url_sign:
                        return suffix
            return 'unknown'
        except:
            return 'unknown'

    @staticmethod
    def downloadFile(getContent, url, context):
        config = context.get('config', {})
        headers = config.get('headers', {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
        })
        method = 'GET'
        post_param = {}
        contentType = headers.get("Content-Type", "")
        matcher = re.search('(@@.*?@@)', url)
        if matcher:
            post_param_str = matcher.group(1)
            if post_param_str:
                method = 'POST'
                query = post_param_str[2:-2]
                params = parse_qs(query)
                post_param = {key: params[key][0] for key in params}
                url = url.replace(post_param_str, '')

        res, resp = False, None
        if method == 'GET':
            res, resp = getContent(url, method=method, headers=headers)
        elif method == 'POST':
            if contentType == '' or contentType == None:
                contentType = 'application/x-www-form-urlencoded; charset=UTF-8'

            if contentType == 'application/json':
                res, resp = getContent(url, method=method, data=json.dumps(post_param),
                                       headers=headers)
            else:
                res, resp = getContent(url, method=method, data=post_param, headers=headers)
        return res, resp

    @staticmethod
    def downloadDetailFile(getContent, url, context, logger):
        taskId = context.get('taskId', 9999999999)
        policyId = context.get('policyId', 'spider')
        config = context.get('config', {})
        res, resp = PageDownloader.downloadFile(getContent, url, context)
        detail_down = []
        if res:
            extension = PageDownloader.detectFileType(url, resp)
            logger.info(f'{url} 检测文件类型: {extension}')
            resp.encoding = 'utf-8'
            html = resp.text
            file_name = f'main.{extension}'
            onDisk = PageDownloader.update_content_size(context, resp, file_name)
            if not onDisk:
                detail_down.append({file_name: html})
            else:
                logger.info(f'{url} 文件大小超过5MB或者所有文件总大小超过10MB, 文件落盘')

            detailConfig = config.get('detail', {})
            downConfig = detailConfig.get('down', {})
            for fileName in downConfig:
                fileRule = downConfig.get(fileName)
                filePaths = FieldParser.parseFieldByRule(html, fileRule)
                filePaths = FieldParser.url_fix(filePaths, context)
                for i, filePath in enumerate(filePaths):
                    res, resp = PageDownloader.downloadFile(getContent=getContent, url=filePath, context=context)
                    if res:
                        extension = PageDownloader.detectFileType(filePath, resp)
                        file_name = f'{fileName}_{i + 1}.{extension}'
                        logger.info(f'{filePath} 检测文件类型: {extension}')

                        onDisk = PageDownloader.update_content_size(context, resp, file_name)
                        if not onDisk:
                            detail_down.append({file_name: resp.content})
                        else:
                            logger.info(f'{filePath} 文件大小超过5MB或者所有文件总大小超过10MB, 文件落盘')
        context['detail_down'] = detail_down

    @staticmethod
    def update_content_size(context, resp, file_name):
        taskId = context.get('taskId', 9999999999)
        policyId = context.get('policyId', 'spider')
        headers = resp.headers
        curr_content_len = int(headers.get('Content-Length', 0))
        if curr_content_len == 0:
            curr_content_len = len(resp.content)

        detail_down_size = context.get('detail_down_size', 0)
        context['detail_down_size'] = detail_down_size + curr_content_len

        if curr_content_len > 1024 * 1024 * 5 or context['detail_down_size'] > 1024 * 1024 * 10:
            if not TaskHomeExist(taskId, policyId):
                createTaskHome(taskId, policyId)
            task_home_dir = getTaskHomePath(taskId, policyId)
            file_path = os.path.join(task_home_dir, file_name)
            with open(file_path, mode='wb') as fw:
                fw.write(resp.content)
            return True
        else:
            return False
