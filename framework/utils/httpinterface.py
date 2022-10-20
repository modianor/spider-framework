import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from framework.config import Client
from framework.core import status, logger


class SpiderHttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        request_path = parsed_path.path
        output = {'success': False, 'status': False}

        try:
            if '/spider/start' in request_path:
                output = self.start()

            if '/spider/stop' in request_path:
                output = self.pause()
        except:
            pass

        self.send_response(200)
        self.send_header("Content-type", "text-html")
        self.end_headers()
        output = json.dumps(output, ensure_ascii=False)
        self.wfile.write(output.encode())
        return

    @staticmethod
    def start():
        status.run = True
        logger.info(f'爬虫进程:{Client.PROCESS_NAME} 版本:{Client.VERSION} 开始调度')
        return {'success': True, 'status': True}

    @staticmethod
    def pause():
        status.run = False
        logger.info(f'爬虫进程:{Client.PROCESS_NAME} 版本:{Client.VERSION} 停止调度')
        return {'success': True, 'status': False}
