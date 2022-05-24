from framework.config.config import BaseConfig
from framework.utils.single import Singleton


@Singleton
class PluginConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.configPath = 'plugins.ini'

    @property
    def section(self):
        return self.config['PLUGIN']

    @property
    def plugins(self):
        plugins_str = self.section.get('plugins')
        policy_modules = plugins_str.split(';')
        plugins = dict()
        for policy_module in policy_modules:
            if policy_module and policy_module != '':
                policy, module = policy_module.split(':')
                plugins[policy] = module
        return plugins
