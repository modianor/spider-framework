from .client import ClientConfig
from .plugin import PluginConfig
from .spider import SpiderConfig

# sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

Client = ClientConfig()
Plugins = PluginConfig()
Spider = SpiderConfig()
