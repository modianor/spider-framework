import configparser
import sys
import os

if __name__ == '__main__':
	# 获取所用的section节点
	config = configparser.ConfigParser()
	config.read("../plugins.ini", encoding="utf-8")
	plugin_section = config['PLUGIN']
	print(plugin_section.get('plugins'))
