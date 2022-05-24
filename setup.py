# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="spider-framework",  # 搜索时，唯一的名字
    version="0.0.1",
    author="modianor",
    url="https://github.com/modianor/spider-framework",
    author_email="modianserver@gmail.com",
    description="spider-framework是一款分布式通用爬虫框架，抽象爬虫抓取模式、任务接口和结构化模式，定义统一的接口规范，是一款将数据抓取与数据结构化解耦的爬虫框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    # 模块相关的元数据
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=[
        'lxml==4.4.1',
        'PyInstaller==5.1',
        'python_Levenshtein==0.12.2',
        'requests==2.23.0'
    ],
    python_requires='>=3',
)
