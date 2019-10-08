#!/usr/bin/env python
# _*_ coding:UTF-8 _*_


import os
import socket

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "127.0.0.1"  #  服务端IP 用于服务端进行绑定使用
PORT = 8080  # 服务端 端口

ADDRESS_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM
ALLOW_REUSE_ADDRESS = True
MAX_PACKET_SIZE = 8192
MAX_SOCKET_LISTEN = 5
CODING = 'utf-8'  # 指定编码类型
USER_HOME_DIR = os.path.join(BASE_DIR, 'home')

ACCOUNT_FILE = os.path.join(BASE_DIR, 'conf', 'accounts.ini')



# 面向对象方式的ftp server\server\bin\luffy_server.py start


