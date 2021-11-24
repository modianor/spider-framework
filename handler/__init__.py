import abc


class BaseHandler(object, metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def handle(self, task_or_result):
		pass
