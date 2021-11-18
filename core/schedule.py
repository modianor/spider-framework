import time

from utils.queue import TaskQueue
from utils.single import singleton


@singleton
class Scheduler(object):
    def __init__(self) -> None:
        self.run = False
        self.policyId = ''
        self.task_queue = TaskQueue()

    def print_status(self):
        while True:
            print('Scheduler is run: ', self.run)
            time.sleep(1)

    def get_task(self):
        pass

# if __name__ == '__main__':
#     scheduler = Scheduler()
#     scheduler.init()
