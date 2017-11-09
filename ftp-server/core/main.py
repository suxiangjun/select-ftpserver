#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author = "susu"
import selectors, socket,json,shelve,os,sys,time,hashlib,logging
import queue
basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
user_basedir=basedir+'/home/'
sys.path.append(basedir)
conn_dic={} #用于存放每个连接上传/下载的文件信息
class My_select(object):
    user_now_dir="/"
    def __init__(self):
        self.sel=selectors.DefaultSelector()
        self.d=queue.Queue()
    def accept(self,sock,mask):
        "接收客户端信息实例"  #{q:[put,get] }
        self.conn, self.addr = sock.accept()
        # 用于存放用户上传文件/下载文件的临时数据
        conn_dic[self.conn]=[{"filesize": 0,"file": queue.Queue(),"uploads":0},{"filesize": queue.Queue(), "file": queue.Queue()}]
        self.conn.setblocking(False)
        self.sel.register( self.conn, selectors.EVENT_READ, self.read)  # 新连接注册read回调函数

    def read(self,conn,mask):
        "接收客户端的数据"
        client_data =self.conn.recv(1024)  # eg: '{"action": "get", "filename": "filename", "overridden": true}'
        if conn_dic[self.conn][0]["uploads"]:  # d 对列有数据代表传输过来的是用户上传的文件的数据，开始执行下载
            q = queue.Queue()
            # 获取put_dic
            put_dic = conn_dic[self.conn][0]
            if os.path.isfile(put_dic["file_dir"] + put_dic["filename"]):
                f = open(put_dic["file_dir"] + put_dic["filename"] + ".new", "wb")
            else:
                f = open(put_dic["file_dir"] + put_dic["filename"], "wb")
            received_size = len(client_data)
            print(received_size)
            f.write(client_data)
            while received_size < put_dic["filesize"]:
                data = self.conn.recv(1024)
                f.write(data)
                received_size += len(data)
            else:
                f.close()
                conn_dic[self.conn][0]["uploads"] = 0  # 关闭上传模式
                info = "file [%s] has uploaded..." % put_dic["filename"]
                self.conn.send(info.encode())
                self.log("成功上传{}文件".format(put_dic["filename"]))
        else:
            if client_data:
                if  client_data.decode().startswith("{"):
                    cmd_dic = json.loads(client_data.decode())
                    action = cmd_dic["action"]
                    if hasattr(self,action):
                        func = getattr(self,action)
                        func(cmd_dic)
                elif client_data.decode().startswith("receive"):
                    self.conn.sendall(conn_dic[self.conn][1]["file"].get())
                elif client_data.decode().startswith("uploads"):
                    conn_dic[self.conn][0]["uploads"]=1  # 激活上传模式
                    self.conn.send(b"ack")
            else:
                print("closing",conn)
                self.sel.unregister(conn)
                conn.close()

    #查看文件
    def ls(self, *args):
        '''查看家目录文件'''
        cmd_dic = args[0]
        user_dir = user_basedir + self.user_now_dir
        filenames = os.listdir(user_dir)
        data = [[], []]
        for i in filenames:
            if os.path.isfile(user_dir + "/" + i):
                data[1].append(i)
            else:
                data[0].append(i)
        self.conn.send(str(data).encode())

    #上传文件
    def put(self,*args):
        '''接收客户端文件'''
        cmd_dic = args[0]
        conn_dic[self.conn][0]["filename"]=cmd_dic["filename"]
        conn_dic[self.conn][0]["filesize"]=cmd_dic["size"]
        conn_dic[self.conn][0]["file_dir"]=user_basedir+self.user_now_dir+"/"
        self.conn.send(b"200 ok")

    #下载文件
    def get(self,*args):
        cmd_dic = args[0]
        get_dic=conn_dic[self.conn][1]
        filename = cmd_dic["filename"]
        user_dir=user_basedir+self.user_now_dir+"/"
        print("{0}下载文件:".format(self.addr[0]))
        self.log("{}下载{}文件".format(self.addr[0], filename))
        if os.path.isfile(user_dir + filename):
            with open(user_dir+filename, "rb") as f:
                file_size = os.stat(user_dir+filename).st_size
                conn_dic[self.conn][1]["filesize"]=file_size
                conn_dic[self.conn][1]["file"].put(f.read())
            self.conn.send(str(file_size).encode())
        else:
            self.conn.send("n".encode())

    #日志模块
    @staticmethod
    def log(info):
        logging.basicConfig(filename=basedir + "/log/" + "ftp.log",
                            level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')
        logging.info(info)

    def run(self):
        server = socket.socket()
        server.bind(('localhost', 9999))
        server.listen(500)
        server.setblocking(False)
        self.sel.register(server, selectors.EVENT_READ, self.accept)  # 注册事件，只要来一个连接就调accept这个函数,
        while True:
            events = self.sel.select()
            print("事件：",events)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

f=My_select()
