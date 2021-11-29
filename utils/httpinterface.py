from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse


class SpiderResquest(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        try:
            params = dict([p.split('=') for p in parsed_path[4].split('&')])
        except:
            params = {}

        print('修改run: ', params['run'])
        self.send_response(200)
        self.send_header("Content-type", "text-html")
        self.end_headers()
        output = "ok"
        self.wfile.write(output.encode())
        return
