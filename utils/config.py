import configparser

from utils.single import Singleton


@Singleton
class PluginConfig:

    def __init__(self) -> None:
        super().__init__()
        self.plugins = dict()
        self.load_config()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read("D:\pycharm_workspace\spider-framework\plugins.ini", encoding="utf-8")
        plugin_section = config['PLUGIN']
        plugins_str = plugin_section.get('plugins')
        policy_modules = plugins_str.split(';')
        for policy_module in policy_modules:
            if policy_module and policy_module != '':
                policy, module = policy_module.split(':')
                self.plugins[policy] = module


if __name__ == '__main__':
    c1 = PluginConfig()
    c2 = PluginConfig()
    print(c1 == c2)
