#!/usr/bin/env python
# _*_ coding:UTF-8 _*_


import hashlib
import configparser
from .import settings

# print(settings.ACCOUNT_FILE)

# def make_md5_on_file(file_path):
#     '''给文件制作md5  每次都要打开文件，要想办法保存到一个位置，当文件发生修改时更新这个md5'''
#     m = hashlib.md5()
#     with open(file_path, 'rb') as f:
#         bytes_str = f.read(1024)
#         while bytes_str != b'':
#             m.update(bytes_str)
#             bytes_str = f.read(1024)
#         md5value = m.hexdigest()
#         return md5value

def make_md5_on_file(file_path):
    '''给文件制作md5  每次都要打开文件，要想办法保存到一个位置，当文件发生修改时更新这个md5'''
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        for line in f:
            bytes_str = line
            m.update(bytes_str)
        md5value = m.hexdigest()
        return md5value

def load_all_user_info():
    '''由FTPserver调用，加载所有的用户数据到内存'''
    confing = configparser.ConfigParser()
    confing.read(settings.ACCOUNT_FILE)
    return confing

