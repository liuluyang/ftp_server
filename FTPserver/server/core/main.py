#!/usr/bin/env python
# _*_ coding:UTF-8 _*_

import socket
import json
import hashlib
import struct
import os
import subprocess
from conf import settings
from conf import config_tool


class FTPServer(object):
    '''处理与客户端所有的交互的 socket server
    所需要的参数，从settings 和 实例化时 传进来'''
    address_family = settings.ADDRESS_FAMILY
    socket_type = settings.SOCKET_TYPE
    allow_reuse_address = settings.ALLOW_REUSE_ADDRESS  # 是否重用端口开关 默认 Fales
    max_packet_size = settings.MAX_PACKET_SIZE  # 最大传输流量8192
    coding = settings.CODING  # utf-8
    request_queue_size = settings.MAX_SOCKET_LISTEN  # 最大挂起数量5
    server_dir = settings.USER_HOME_DIR  # 总家目录

    STATUS_CODE = {
        0: 'normal ',
        100: 'ls Error info',
        101: 'current dir has no file at all',
        200: 'Username Password Authentication Successful!',
        201: 'wrong username or password',
        300: 'The file was not find',
        301: 'find the file',
        302: 'The server did not receive the complete data',
        303: 'The server receive the complete data',
        400: 'The dirname was not find',
        401: 'Has entered this directory',
        500: "It's already on the top floor"
    }

    def __init__(self, management_instance, bind_and_acttivate=True):  # 在management类中start的位置，将management的实例传进来
        '''构造函数，可扩展 不可覆盖'''
        self.management_instance = management_instance  # 类的构造函数中，接收这个参数，这样就能够使用到传进来的实例的对象中的属性
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.config_obj = config_tool.load_all_user_info()  #
        if bind_and_acttivate:
            try:
                self.server_bind()
                self.server_activate()
            except:
                self.server_close()
                raise

    def server_bind(self):
        """由构造函数调用以绑定套接字"""
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((settings.HOST, settings.PORT))
        self.server_address = self.socket.getsockname()

    def server_activate(self):
        """由构造函数调用以激活服务器 """
        self.socket.listen(self.request_queue_size)

    def get_request(self):
        """从套接字获取请求和客户机地址。 """
        return self.socket.accept()

    def server_close(self):
        """调用以清理服务器。 """
        self.socket.close()

    def close_request(self, request):
        """调用以清除单个请求"""
        request.close()

    def run_forever(self):
        '''启动socket server 运行到天荒地老'''
        print('starting luffyFTP server on %s:%s'.center(50, '-') % (settings.HOST, settings.PORT))
        while True:
            self.request, self.client_addr = self.get_request()
            # print(self.request, self.cline_addr)
            self.handle()

    def handle(self):
        '''接收客户端发来的报头 解析之后 进行相应的操作'''
        while True:
            try:
                raw_data = self.request.recv(4)
                if not raw_data:
                    # print('client %s disconnection' % self.client_addr)
                    # del self.request, self.client_addr
                    break
                data_len = struct.unpack('i', raw_data)[0]
                date_json = self.request.recv(data_len).decode(self.coding)
                data_dic = json.loads(date_json)
                action_type = data_dic.get('action_type')
                if action_type:  # 不能为空
                    if hasattr(self, "_%s" % action_type):
                        func = getattr(self, "_%s" % action_type)
                        func(data_dic)
            except Exception:
                break

    def send_response(self, status_code, *args, **kwargs):
        '''打包发送状态码消息给客户端'''
        data = kwargs
        data['status_code'] = status_code
        data['status_msg'] = self.STATUS_CODE[status_code]
        bytes_data = json.dumps(data).encode('utf-8')
        head_struct = struct.pack('i', len(bytes_data))

        self.request.send(head_struct)   # 这里时通信循环干的事情了，一定要是self.request
        self.request.send(bytes_data)

    def authentication(self, username, password):
        '''对用户名密码进行验证'''
        if username in self.config_obj:
            _password = self.config_obj[username]['password']
            md5_obj = hashlib.md5()
            md5_obj.update(password.encode('utf-8'))
            if md5_obj.hexdigest() == _password:
                return True
            else:
                return False
        else:
            return False

    def _auth(self, data):
        '''处理用户认证请求'''
        if self.authentication(data.get('username'), data.get('password')):
            self.home_dir = os.path.join(self.server_dir, data.get('username'))
            self.userhome_dir = os.path.join(self.server_dir, data.get('username'))
            self.send_response(status_code=200,)
        else:
            self.send_response(status_code=201)

    def _put(self, data):
        '''用户进行上传'''
        file_path = os.path.normpath(os.path.join(self.userhome_dir, data['filename']))
        filesize = data['filesize']
        recv_size = 0
        m = hashlib.md5()
        with open(file_path, 'wb') as f:
            while recv_size < filesize:
                recv_data = self.request.recv(self.max_packet_size)
                f.write(recv_data)
                recv_size += len(recv_data)

                bytes_str = recv_data
                m.update(bytes_str)
            md5value = m.hexdigest()
            if md5value == data['md5value']:
                self.send_response(status_code=303)
            else:
                self.send_response(status_code=302)

    def _get(self, data):
        '''用户进行下载'''
        file_path = os.path.normpath(os.path.join(self.userhome_dir, data['filename']))
        if not os.path.isfile(file_path):
            self.send_response(status_code=300)
        else:
            filesize = os.path.getsize(file_path)
            md5value = config_tool.make_md5_on_file(file_path)
            self.send_response(status_code=301, filesize=filesize, md5value=md5value, filename=data['filename'])
            send_size = 0
            with open(file_path, 'rb') as f:
                for line in f:
                    self.request.send(line)
                    send_size += len(line)

    def _ls(self, data):
        '''给客户端显示当前文件下有哪些内容'''
        cmd_boj = subprocess.Popen('dir %s' % self.userhome_dir, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        stdout = cmd_boj.stdout.read()
        stderr = cmd_boj.stderr.read()
        cmd_result = (stdout + stderr).decode('GBK')
        if not cmd_result:
            self.send_response(status_code=101)
        else:
            self.send_response(status_code=0, dir_info=cmd_result)

    def _cd(self, data):
        '''进入用户想要进入的目录当中'''
        dirname = data['dirname']
        if not dirname.startswith('.'):
            if os.path.isdir(os.path.join(self.userhome_dir, dirname)):
                self.userhome_dir = os.path.join(self.userhome_dir, dirname)
                self.client_dir = self.userhome_dir.replace(settings.USER_HOME_DIR, '')
                self.send_response(status_code=401, dirn=self.client_dir)
            else:
                self.send_response(status_code=400)
        else:
            li = dirname.split('\\')
            count = 0
            while count < len(li):
                '''循环 如果 当前路径 已经到用户的家目录，就返回500 已经到达最顶层'''
                if self.userhome_dir == self.home_dir:
                    self.send_response(status_code=500)
                else:
                    self.userhome_dir = os.path.dirname(self.userhome_dir)
                    self.client_dir = self.userhome_dir.replace(settings.USER_HOME_DIR, '')
                    self.send_response(status_code=0, dirn=self.client_dir)
                count += 1

    def _make_dir(self):
        '''创建用户想要创建的文件夹'''
        print('创建用户想要创建的文件夹')

