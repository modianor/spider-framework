from threading import Thread


class FetcherThread(Thread):

	def __init__(self, fetcherInstance, threadName, **kwds):
		Thread.__init__(self, **kwds)
		self.fetcherInstance = fetcherInstance
		self.threadName = threadName
		self.parentThread = None
		self.childThreads = list()

	def __checkChildThreads__(self):
		childThreadNum = 3
		if len(self.childThreads) < childThreadNum:
			for i in range(childThreadNum):
				childThread = FetcherThread(self.fetcherInstance, f'{self.threadName}_child_thread_{i + 1}')
				self.childThreads.append(childThread)

	def run(self) -> None:
		pass


class TaskHandler(object):
	def __init__(self) -> None:
		self.fetcherHandler = dict()
