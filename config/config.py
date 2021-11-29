import configparser


class BaseConfig(object):
    def __init__(self) -> None:
        super().__init__()
        self.configPath = ''

    @property
    def config(self):
        config = configparser.ConfigParser()
        config.read(self.configPath, encoding="utf-8")
        return config