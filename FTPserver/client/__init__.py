#!/usr/bin/env python
# _*_ coding:UTF-8 _*_

import subprocess
import re

courrentdir = r'D:\Homework_exercises\FTPserver\client\donwload'
n = subprocess.Popen('cd D:\Homework_exercises\FTPserver\client\donwload', shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
stdout = n.stdout.read()
stderr = n.stderr.read()
current = stdout + stderr
print(current.decode('GBK'))

dirname = 'file'
if not dirname.startswith('..'):
    print(123456)



