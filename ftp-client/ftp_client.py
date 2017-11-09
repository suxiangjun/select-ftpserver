#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author = "susu"
import socket
#!/usr/bin/env python
#-*- coding:utf-8 -*-
import json
import socket,os,sys,time
basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
class FtpClient(object):
    def __init__(self):
        self.client=socket.socket()
        self.now_dir=None
    def help(self):
        msg='''
ls           #查看文件
get filename #下载文件
put filename #上传文件
q            #退出程序  
        '''
        print(msg)
    def connect(self,ip,port):
        self.client.connect((ip, port))
        self.help()
        self.interactive()
    #上传文件
    def cmd_put(self,*args):
        cmd_split=args[0].split()
        if len(cmd_split)>1:
            filename=cmd_split[1]
            if os.path.isfile(filename):
                filesize=os.stat(filename).st_size
                msg_dic={
                    "action":"put",
                    "filename":filename,
                    "size":filesize
                }
                self.client.send(str(json.dumps(msg_dic)).encode("utf-8"))
                server_response=self.client.recv(1024)
                if server_response.decode().startswith("200"):
                    self.client.send(b"uploads")
                    self.client.recv(1024)
                    f=open(filename,"rb")
                    data=f.read()
                    self.client.sendall(data)
                    print(self.client.recv(1024).decode())
                    f.close()

    #下载文件
    def cmd_get(self,*args):
        cmd_split=args[0].split()
        if len(cmd_split)>1:
            filename=cmd_split[1]
            msg_dic={
                    "action":"get",
                    "filename":filename,
                    "overridden":True
                }
            self.client.send(str(json.dumps(msg_dic)).encode("utf-8"))
            server_respose = self.client.recv(1024)
            if server_respose.decode().isdigit():
                print("文件大小: %s bytes"%server_respose.decode() )
                file_total_size = int(server_respose.decode())
                self.client.send(b"receive files")
                revived_size = 0
                with open(filename, "wb") as f:
                    while revived_size < file_total_size:
                        data = self.client.recv(1024)
                        revived_size += len(data)
                        f.write(data)
                        sys.stdout.write("\r{}>%{}".format("="*int(revived_size/file_total_size*100),int(revived_size*100/file_total_size)))
                        sys.stdout.flush()
                    else:
                        print("file recv done")
            else:
                print("文件不存在")

    #查看文件
    def cmd_ls(self,*args):
        msg_dic = {
            "action": "ls"
        }
        self.client.send(str(json.dumps(msg_dic)).encode("utf-8"))
        allfile=eval(self.client.recv(1024).decode())
        if allfile[0]:
            if len(allfile[0])>1:
                for j in allfile[0]:
                    print("\33[31m%s\33[0m" % j)
            else:
                print("\33[31m%s\33[0m" % allfile[0][0])
        if allfile[1]:
            if len(allfile[1])>1:
                for k in allfile[1]:
                    print(k)
            else:
                print(allfile[1][0])
    #交互界面
    def interactive(self):
        while True:
            cmd=input(">>").strip()
            if len(cmd)==0 or cmd=="cd":continue
            elif cmd=="q":sys.exit()
            cmd_str=cmd.split()[0]
            if hasattr(self,"cmd_%s"%cmd_str):
                func=getattr(self,"cmd_%s"%cmd_str)
                func(cmd)
            else:
                self.help()
c=FtpClient()
c.connect("localhost",9999)
