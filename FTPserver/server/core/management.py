#!/usr/bin/env python
# _*_ coding:UTF-8 _*_


from core import main

class ManagementTool(object):
    '''负责对 用户输入的指令，进行解析。并调用相应的模块处理'''
    def __init__(self, sys_argv):
        self.sys_argv = sys_argv
        self.verification()

    def verification(self):
        '''由构造函数调用 验证用户输入的指令是否合法，如果不合法。打印帮助信息'''
        if len(self.sys_argv) < 2:  # sys.argv 列表中默认会带上文件名，所以长度必须不能小于2
            self.help_msg()
        cmd = self.sys_argv[1]
        if not hasattr(self, cmd):
            print('无效语法')
            self.help_msg()

    def help_msg(self):
        msg = '''
        start       start FTP server
        stop        stop FTP server
        restart     restart FTP server
        createuser  username  create a ftp user
        其余功能还没扩展呢'''
        exit(msg)  # 如果命令输入的是错误的，就退出程序。因为 如果继续向后走的话，会因为没有这个命令报错。
        # 虽然可以，加上循环。让用户继续输入。不过 再来一次就好了。没必要那么麻烦

    def execute(self):
        '''进行解析并执行指令，写在这里可以进行扩展'''
        cmd = self.sys_argv[1]
        func = getattr(self, cmd)
        func()   # 这里并没有传参数，因为sys.argv 是构造函数中的，相当于类中的一个全局变量。
        # 其余函数 直接调用就好了，不需要还要在这里传参数

    def start(self):
        '''启动FTP server'''
        server = main.FTPServer(self)  # FTPServer 有可能用到当前这个程序的一些东西，那么就把实例本身
        server.run_forever()            # 当作一个参数 传给FTPServer  那就可以在FTPServer中使用这个类中的属性了

    def stop(self):
        '''这是停止服务'''
        print('停止服务了')

    def restart(self):
        '''重新启动服务器'''
        print('重新启动服务器')

    def createuser(self):
        '''管理员创建用户使用的'''
        print('管理员专用')


        #D:\Homework_exercises\FTPserver\server\bin>python luffy_server.py start
