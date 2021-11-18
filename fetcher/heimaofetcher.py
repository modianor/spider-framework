import logging

from fetcher import Fetcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s:%(lineno)d] %(levelname)s: %(message)s')


class HeiMaoFetcher(Fetcher):

    def __init__(self) -> None:
        super().__init__()
        self.policyId = 'heimaotousu'
        self.logger = logging.getLogger(self.policyId)

    def getList(self, task):
        self.logger.info('run getList method...')
        pass

    def getDetail(self, task):
        self.logger.info('run getDetail method...')
        pass

    def getData(self, task):
        self.logger.info('run getData method...')
        pass
