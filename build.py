# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.__main__ import run


def copy_function(src, target):
    with open(src, 'rb') as rstream:
        container = rstream.read()
        with open(target, 'wb') as wstream:
            wstream.write(container)


run(pyi_args=['build.spec'])
copy_function(r'framework/client.ini', r'./dist/client.ini')
copy_function(r'framework/plugins.ini', r'./dist/plugins.ini')
