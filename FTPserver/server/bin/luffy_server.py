#!/usr/bin/env python
# _*_ coding:UTF-8 _*_


import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 入口程序必须先 指定 基础目录。以便于其余的调用程序，可以通过这个路径，进行相对的导入
sys.path.append(BASE_DIR)  # 将基础目录添加到，路径列表中

if __name__ == '__main__':
    from core import management
    # print()
    # sys.argv 把用户终端输入的命令，拿到并把拿到的列表，交给 解析命令的类。传给__init__了
    argv_parser = management.ManagementTool(sys.argv)
    argv_parser.execute()










