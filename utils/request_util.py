from utils.single import Singleton


@Singleton
class MyRequest(object):

	def __init__(self) -> None:
		super().__init__()

