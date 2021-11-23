import threading
from http.server import HTTPServer

from core.schedule import Scheduler
from utils.httpinterface import Resquest


class Engine(object):
	scheduler = Scheduler()

	def start_http_server(self):
		host = ('localhost', 8888)
		server = HTTPServer(host, Resquest)
		print("Starting server, listen at: %s:%s" % host)
		server.serve_forever()

	def init(self):
		t1 = threading.Thread(target=self.start_http_server, args=())  # 创建线程
		t1.start()  # 开启线程

		t2 = threading.Thread(target=self.scheduler.print_status, args=())  # 创建线程
		t2.start()  # 开启线程
