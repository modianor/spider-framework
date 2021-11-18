import configparser
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
# sys.path.append(os.path.join(os.path.abspath(os.path.join(os.getcwd(), "..")), 'common'))
if __name__ == '__main__':
    # 获取所用的section节点
    config = configparser.ConfigParser()
    config.read("plugins.ini", encoding="utf-8")
    print(config.sections())
    # 运行结果
    # ['db', 'concurrent']
