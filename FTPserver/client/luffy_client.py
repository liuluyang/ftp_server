#!/usr/bin/env python
# _*_ coding:UTF-8 _*_


import socket
import optparse
import json
import struct
import os
import sys
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from conf import settings
donwload_dir = settings.FILE_PATH

class FTPClient(object):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    allow_reuse_address = True
    max_pack_size = 8192
    request_queue_size = 5
    coding = 'utf-8'

    def __init__(self, connect=True):
        ''' elf.options 这是这个模块生成的一个字典 self.args  这是用户输入的命令。和sys.argv 差不多
            如果用户按照规则输入，那么相应的值 就会在字典中显示， 不按规则输入的值，就放倒了列表中'''
        parser = optparse.OptionParser()
        parser.add_option("-s", "--server", dest='server', help="ftp server ip_addr")
        parser.add_option("-P", "--port", type="int", dest="port", help="ftp server port")
        parser.add_option("-u", "--username", dest="username", help="username info")
        parser.add_option("-p", "--password", dest="password", help="password info")
        self.options, self.args = parser.parse_args()
        self.current_dir = None
        print(self.options, self.args)
        self.argv_verification()  # 判断合法性
        self.socket = self.make_connection()  # 建立连接
        if connect:
            try:
                self.client_connect()
            except:
                self.client_close()
                raise

    def argv_verification(self):
        '''判断用户输入的合法性'''
        if not self.options.server or not self.options.port:
            exit('必须提供，ip 和 端口')

    def make_connection(self):
        '''由构造函数调用生成 socket 对象'''
        self.socket = socket.socket(self.address_family, self.socket_type)
        return self.socket

    def client_connect(self):
        '''由构造函数直接调用，激活客户端，连接服务端'''
        self.socket.connect((self.options.server, self.options.port))  #

    def client_close(self):
        '''由构造函数调用，关闭客户端'''
        self.socket.close()

    def auth(self):
        '''输入账户名，密码。服务端验证完成后，根据接收到的状态码，返回 Ture or False'''
        count = 0
        while count < 3:
            username = input('username:').strip()
            if not username: continue
            self.current_dir = '\\' + username
            pwd = input('password:').strip()
            cmd = {
                'action_type': 'auth',
                'username': username,
                'password': pwd
            }

            self.send_head(cmd)
            head_dic = self.recv_head()
            if head_dic['status_code'] == 200:
                return True
            else:
                count += 1
                print(head_dic['status_msg'])
                continue

    def send_head(self, cmd):
        '''发送客户端的报头，'''
        client_head_bytes = json.dumps(cmd).encode(self.coding)
        client_head_len = struct.pack('i', len(client_head_bytes))
        self.socket.send(client_head_len)
        self.socket.send(client_head_bytes)

    def recv_head(self):
        '''接收服务端发来的报头'''
        obj = self.socket.recv(4)
        header_size = struct.unpack('i', obj)[0]
        header_json = self.socket.recv(header_size).decode(self.coding)
        header_dict = json.loads(header_json)
        return header_dict

    def put(self, *args):
        '''上传文件'''
        cmd = args[0]
        filename = args[1]
        if not os.path.isfile(os.path.join(donwload_dir, filename)):
            print('file %s 不在donwload文件中' % filename)
            return
        else:
            filesize = os.path.getsize(os.path.join(donwload_dir, filename))
            md5value = make_md5_on_file(os.path.join(donwload_dir, filename))
            head_dic = {'action_type': cmd, 'filesize': filesize, 'filename': filename, 'md5value': md5value}
            self.send_head(head_dic)

        send_size = 0
        with open(os.path.join(donwload_dir, filename), 'rb') as f:
            for line in f:
                self.socket.send(line)
                send_size += len(line)
                progres(send_size, filesize)
            else:
                print('数据发送成功')
        header_dict = self.recv_head()
        print(header_dict['status_msg'])

    def get(self, *args):
        '''下载文件'''
        cmd = args[0]
        filename = args[1]
        client_head_dic = {'action_type': cmd, 'filename': filename}
        self.send_head(client_head_dic)
        server_head_dic = self.recv_head()
        if server_head_dic['status_code'] == 300:
            print(server_head_dic['status_msg'])
            return
        file_path = os.path.join(donwload_dir, server_head_dic['filename'])
        recv_size = 0
        m = hashlib.md5()
        with open(file_path, 'wb') as f:
            while recv_size < server_head_dic['filesize']:
                line = self.socket.recv(self.max_pack_size)
                f.write(line)
                recv_size += len(line)

                bytes_str = line
                m.update(bytes_str)

                progres(recv_size, server_head_dic['filesize'])  # 进度条
            md5value = m.hexdigest()
            if md5value == server_head_dic['md5value']:
                print('文件完整')
        print()

    def ls(self, *args):
        '''显示当前目录下的文件'''
        cmd = args[0]
        client_head_dic = {'action_type': cmd}
        self.send_head(client_head_dic)
        server_head_dic = self.recv_head()
        if server_head_dic['status_code'] == 0:
            print(server_head_dic['dir_info'])
        if server_head_dic['status_code'] == 100:
            print(server_head_dic['dir_info'])

    def cd(self, *args):
        '''切换目录'''
        cmd = args[0]
        dirname = args[1]
        if dirname != '.':
            client_head_dic = {'action_type': cmd, 'dirname': dirname}
            self.send_head(client_head_dic)
            server_head_dic = self.recv_head()
            if server_head_dic['status_code'] == 400:
                print(server_head_dic['status_msg'])
            elif server_head_dic['status_code'] == 401:
                print(server_head_dic['status_msg'])
                self.current_dir = server_head_dic['dirn']
            elif server_head_dic['status_code'] == 0:
                self.current_dir = server_head_dic['dirn']
        else:
            print('输入错误')
            return

    def make_dir(self, *args):
        '''在自己的目录下，创建文件夹'''
        print('在自己的目录下，创建文件夹')

    def help_msg(self, *args):
        msg = '''command error!!!
        Correct format:
        get filename 下载文件
        put filename 上传文件
        ls  显示当前所在目录下的文件和子目录
        cd dirname 切换到那个目录下'''
        print(msg)

    def interactive(self):  # 交互函数
        '''处理 与 服务端 的所有交互,解析用户输入的指令'''
        if self.auth():
            while True:
                inp = input('[%s] Q退出：' % self.current_dir).strip()
                if not inp: continue
                cmds = inp.split()
                if inp != 'Q':
                    if hasattr(self, cmds[0]):
                        func = getattr(self, cmds[0])
                        func(*cmds)
                    else:
                        self.help_msg()
                        continue
                else:
                    exit('谢谢使用')



def humanbytes(B):
    '''这传代码 抄来的  T_T '''
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B/KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B/MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B/GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B/TB)

def progres(recv_size, total_size):
    bar_length = 50
    percent = float(recv_size) / float(total_size)
    hashes = '=' * int(percent * bar_length)
    spaces = ' ' * (bar_length - len(hashes))

    sys.stdout.write("\r传输中: [%s] %d%%  %s/%s " % (hashes + spaces, percent * 100,
                                                   humanbytes(recv_size), humanbytes(total_size)))
    sys.stdout.flush()


def make_md5_on_file(file_path):
    '''给文件制作md5  每次都要打开文件，要想办法保存到一个位置，当文件发生修改时更新这个md5'''
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        for line in f:
            bytes_str = line
            m.update(bytes_str)
        md5value = m.hexdigest()
        return md5value


if __name__ == '__main__':
    client = FTPClient()
    client.interactive()





# python luffy_client.py -s 127.0.0.1 -P 8080
# 面向对象方式的ftp server