from utils.single import Singleton


@Singleton
class Status(object):

	def __init__(self) -> None:
		self.userName = ""
		self.token = ""
		self.run = False
