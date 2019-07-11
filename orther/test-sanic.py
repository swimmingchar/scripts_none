#!/usr/bin/env python
# -*- coding:utf-8 -*-

import zipfile,json
import os, sys, re, socket
from multiprocessing import Process
import requests

import paramiko
import aiohttp
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import html, json, redirect
app = Sanic()

# 备份文件备份文件，需要应用名+IP+
def back_file(appname, regx, t_data,con_host):
    global mypath
    global ip

    # TODO 写入传递参数到日志中
    file_path = "/home/tomcat/logs/"
    file_list = list()


    zip_full_path = mypath + "/zipfile/" + appname + t_data + ".zip"
    for f_item in os.listdir(file_path):
        #res = re.search('.*2019.?03.?03.*',f_item)
        res = re.search(regx,f_item)
        if res != None:
            file_list.append(f_item)
    zipfile_obj = zipfile.ZipFile(zip_full_path, 'w',zipfile.ZIP_DEFLATED)
    for item in file_list:
        zipfile_obj.write(file_path+item, item)
        # TODO 写入日志，写入压塑的文件有那系诶，最好带上文件大小
    zipfile_obj.close()
    # 备份路径为：/backup/type/2019/02/boss-core/10.10.3.85/boss-core-20190217.zip
    tran_path = "/backup/type/" + t_data[:4] + "/" + t_data[4:6] + "/" + appname + "/" + ip + "/" + appname + t_data + ".zip"
    local_path = zip_full_path
    # 调用传输模块
    trans_zip(con_host,local_path,tran_path)


# c传输文件
def trans_zip(trans_ip,local_path,trans_path):
    global mypath
    global app_name
    global ip
    # SSH 传输文件
    ssh = paramiko.SSHClient()
    # key = paramiko.RSAKey.from_private_key(os.path.expanduser(mypath + '/.temp.key'))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname=trans_ip , username="tomcat", key_filename=mypath + "/.temp.key")
        t = ssh.get_transport
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(local_path, trans_path)
        # TODO 文件传输完成
    except Exception as msg:
        print("文件传输出错 %s"%msg)
        pass
    sftp.close()
    zipfile = zipfile.ZipInfo(local_path)
    # 返回服务端数据
    j_data = {'appname':app_name,"clientip":ip,"file_name":local_path.split("/")[-1],"file_size":zipfile.compress_size}
    url = "http://" + trans_ip+":10871/zipinfo"
    try:
        url_get = requests.get(url, params=j_data, timeout=5)
    except Exception as msg:
        print("推送错误:%s"%msg)
        pass
    # TODO logs
    print(url_get.json())

    
@app.route("/backfile")
async def backfile(request):
    pra_key = request.args.get('pra_key')
    con_host = request.args.get('con_host')
    app_name = request.args.get('appname')
    regx = request.args.get('regx')
    t_dete = request.args.get('date')
    ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))

    try:
        with open(mypath + ".temp.key","w") as f:
            f.writelines(pra_key)
    except Exception as msg:
        # TODO Error logs
        pass

    # 另起线程调用备份功能
    p = Process(target=back_file, args=(app_name,regx,t_date,con_host))
    p.start()
    
    # 返回 内容
    return json({"query_string": request.query_string})


if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=8000)
    # 写入私钥
    mypath = os.path.dirname(os.path.realpath(__file__))

    if not os.path.exists(mypath + "/zipfile/"):
        os.makedir(mypath + "/zipfile/")
    if not os.path.exists(mypath + "/logs/"):
        os.makedir(mypath + "/logs/")

    # 开启监听客户端监听
    app.run(host="0.0.0.0", port=10870)

#eg：
# curl 'http://172.10.1.31:8000/backfile?con_host=172.10.1.32&pra_key=rerere%20asdfsdfsd'
# {
# 	"con_host": "172.10.1.32",
# 	"pra_key": "rerere asdfsdfsd",
# 	"args2": {
# 		"con_host": ["172.10.1.32"],
# 		"pra_key": ["rerere asdfsdfsd"]
# 	},
# 	"url": "http:\/\/172.10.1.31:8000\/backfile?con_host=172.10.1.32&pra_key=rerere%20asdfsdfsd",
# 	"query_string": "con_host=172.10.1.32&pra_key=rerere%20asdfsdfsd"
# }