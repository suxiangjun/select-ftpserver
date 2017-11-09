## 项目名称：selectors版ftp

*本软件只在python3环境下运行。*

#### 实现功能

- 使用SELECTORS模块实现并发简单版FTP

- 允许多用户并发上传下载文件

  ​

#### 程序架构

```php+HTML
├──ftp-client                # 客户端
│      └──ftp_client.py          #  ftp客户端执行程序     
│                   
│
├──ftp-server                #服务端
│      │──bin                       
│      │   ├──myftp.py      #  ftp服务端执行程序   
│      │   └──__init__.py
│      │──core                       
│      │   ├──main.py      #  主程序   
│      │   └──__init__.py
│      │──home               # 文件存放路径
│      └──log                # 日志目录
│          ├──ftp.log        # 操作日志
│          └──__init__.py
│──README
```

`注意事项：`下载/上传的文件，和客户端程序所在目录相同

[博客地址]: http://www.cnblogs.com/xiangjun555

