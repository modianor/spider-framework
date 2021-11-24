from core.schedule import Scheduler


class Spider(object):
    scheduler = Scheduler()

    def start(self):
        pass

    def pause(self):
        pass

    def getPolicyInfos(self):
        pass

    def init(self):
        self.scheduler.initSchedule()
