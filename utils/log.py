import logging
import os
from logging.handlers import RotatingFileHandler


class Logger(object):
    def __init__(self, logger=None):
        '''
            指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        '''

        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        fmt = '%(asctime)s [%(name)s:%(lineno)d] %(levelname)s: %(message)s'
        format_str = logging.Formatter(fmt)

        log_dir = './log'

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        fh = RotatingFileHandler(f'{log_dir}/{logger}.log', maxBytes=1024 * 1024 * 10, backupCount=3, encoding="utf-8")
        fh.setFormatter(fmt=format_str)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        ch.setFormatter(format_str)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        #  添加下面一句，在记录日志之后移除句柄
        # self.logger.removeHandler(ch)
        # self.logger.removeHandler(fh)
        # 关闭打开的文件
        # fh.close()
        # ch.close()

    def getlog(self):
        return self.logger
