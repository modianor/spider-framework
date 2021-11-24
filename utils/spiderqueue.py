from queue import Queue

from utils.single import Singleton


class BaseQueue(Queue):
    pass


class TaskQueue(BaseQueue):
    def size(self):
        return self.qsize()

    def putTask(self, task):
        self.put(task)

    def getTask(self):
        return self.get()

    def isEmpty(self):
        return self.size() == 0


@Singleton
class ResultQueue(BaseQueue):
    def size(self):
        return self.qsize()

    def putResult(self, result):
        self.put(result)

    def getResult(self):
        return self.get()

    def isEmpty(self):
        return self.size() == 0
