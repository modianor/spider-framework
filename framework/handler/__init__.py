import abc


class BaseHandler(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def createHandlerProcess(self):
        pass
