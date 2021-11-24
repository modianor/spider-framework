from core.schedule import Scheduler


class Spider(object):
	def __init__(self) -> None:
		self.scheduler = Scheduler()

	def start(self):
		pass

	def pause(self):
		pass

	def getPolicyInfos(self):
		pass

	def init(self):
		self.scheduler.initSchedule()
