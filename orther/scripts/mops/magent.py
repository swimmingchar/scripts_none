#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import os
import json
import socket
import logging
import zipfile
import paramiko
import requests
import subprocess
from logging import handlers
from multiprocessing import Process
from apscheduler.schedulers.background import BackgroundScheduler

from sanic import Sanic
# from sanic.exceptions import NotFound
from sanic.log import logger as slogger
from sanic.response import html, json, redirect
app = Sanic()

try:
    os.makedirs(os.path.dirname(os.path.realpath(__file__)) + '/logs/')
except Exception:
    pass

# 日志logger初始化
opslog = logging.Logger('magent')
fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                        datefmt='%Y%m%d %H:%M:%S,')

hd = handlers.TimedRotatingFileHandler('logs/magent.log', when='midnight')
hd.setLevel(logging.INFO)
hd.setFormatter(fmt)
hd.suffix='%Y%m%d-%H%M%S'
opslog.addHandler(hd)


# 备份文件备份文件，需要应用名+IP+
def back_file(appname, regx, t_data, con_host, local_ip, pra_key):
    global zipfile_ok

    # 初始化参数,日志路径和日志文件列表
    file_path = "/home/tomcat/logs/"
    file_list = list()

    # local_ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    zip_full_path = mypath + "/zipfile/" + appname + '_' + t_data + ".zip"
    for f_item in os.listdir(file_path):
        # res = re.search('.*2019.?03.?03.*',f_item)
        # opslog.info("正则表达式为:%s,列表为:%s" % (regx, f_item))
        res = re.search(r'' + str(regx) + '', f_item)
        if res is not None:
            file_list.append(f_item)
    opslog.info("需要压缩的文件有\n%s" % file_list)

    for item in file_list:
        full_path = file_path + item
        if os.path.isfile(full_path):
            zipfile_ok = True

    if zipfile_ok:
        zipfile_obj = zipfile.ZipFile(zip_full_path, 'w', zipfile.ZIP_DEFLATED)
        for item in file_list:
            full_path = file_path + item
            if os.path.isfile(full_path):
                zipfile_obj.write(file_path + item, item)
            # TODO 文件夹压缩
            # elif os.path.isdir(full_path):
            #     zipfile_obj.write(file_path + item + '/*', item + '/*')
        zipfile_obj.close()

        # 备份路径为：/backup/type/2019/02/boss-core/10.10.3.85/boss-core-20190217.zip
        tran_path = "/backup/typeback/" + t_data[:4] + "/" + t_data[4:6] + "/" + appname + "/" + local_ip + "/" + \
            appname + t_data + ".zip"
        # 调用传输模块
        trans_zip(appname, local_ip, con_host, zip_full_path, tran_path, pra_key, file_list)
    if not zipfile_ok:
        opslog.info("没有需要压缩的文件！")


# 传输文件
def trans_zip(appname, local_ip, trans_ip, local_path, trans_path, pra_key, list_file):
    pra_key = str(pra_key).strip()
    t = paramiko.Transport(trans_ip, 22)
    t.banner_timeout = 300
    res = True
    # paramiko.util.log_to_file('logs/magent.log')
    remote_path = '/'+'/'.join(trans_path.split('/')[1:-1])

    try:
        # 使用ssh方式新建目录
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=trans_ip, username='tomcat', port=22,password=pra_key)
        try:
            ssh.exec_command('mkdir -p %s ' % remote_path )
        except FileExistsError:
            pass
        ssh.close()

        t.connect(username='tomcat', password=pra_key)
        sftp = paramiko.SFTPClient.from_transport(t)
        # sftp.mkdir(remote_path)
        sftp.put(local_path, trans_path)
        sftp.close()
        opslog.info("文件传输完成,本地路径:%s。远端路径:%s." % (local_path, trans_path))
    except Exception as e_msg:
        opslog.info("%s 文件传输错误,错误内容为%s" % (local_path.split('/')[-1], e_msg))
        res = False

    # 返回服务端数据
    if res :
        j_data = {'appname': appname, "clientip": local_ip, "file_name": trans_path, 'REV': 'OK'}
    else:
        j_data = {'appname': appname, "clientip": local_ip, "file_name": trans_path, 'REV': 'FAIL'}
    url = 'http://10.10.10.23:10871/zipinfo'

    opslog.info('j_data:%s' % j_data)
    try:
        url_get = requests.get(url, params=j_data, timeout=5)
        opslog.info("传输返回信息：%s" % url_get.json())
    except Exception as msg:
        opslog.info("传输完成回传信息反馈失败，文件名：%s。错误内容：%s" % (local_path.split('/')[-1], msg))
    if res:
        del_zipfile("NOW", list_file)


# 删除N天前的备份日志
def del_zipfile(d_date="7", f_list=None):
    if d_date != "NOW":
        cmd = 'find ' + mypath + '/zipfile/ -type f -mtime +' + str(d_date) + '| xargs rm -f'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for i in p.stdout.readlines():
            i = i.decode(encoding='utf-8').split('\n')[0]
            opslog.info("本次删除文件为：%s" % i)
            p.stdout.close()

        for i in p.stderr.readlines():
            i = i.decode(encoding='utf-8').split('\n')[0]
            opslog.info("本次删除失败的文件为：%s" % i)
            p.stderr.close()
    if d_date == "NOW" and zipfile_ok:
        for i in f_list:
            cmd = 'rm -f /home/tomcat/logs/' + i
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for f_line in p.stdout.readlines():
                f_line = f_line.decode(encoding='utf-8').split('\n')[0]
                opslog.info("本次删除文件为：%s" % f_line)
                p.stdout.close()

            for f_line in p.stderr.readlines():
                f_line = f_line.decode(encoding='utf-8').split('\n')[0]
                opslog.info("%s 可能为文件夹"% f_line)
                p.stderr.close()
    if not zipfile_ok:
        opslog.info("此次没有成功压缩文件！")


@app.route("/m_status")
async def m_status(request):
    status = request.args.get('status')

    if str(status).strip().lower() == 'stop':
        app.stop()
        exit()


@app.route("/backfile")
async def backfile(request):
    pra_key = request.args.get('pra_key')
    con_host = request.args.get('con_host')
    app_name = request.args.get('appname')
    regx = request.args.get('regx')
    t_date = request.args.get('date')
    local_ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))

    opslog.info("应用名：%s\nIP地址：%s\n时间:%s\nregx:%s" % (app_name,
                                                            str(con_host),
                                                            str(t_date),
                                                            str(regx)))
    # 另起线程调用备份功能
    p = Process(target=back_file, args=(app_name, regx, t_date, con_host, local_ip, pra_key))
    p.start()

    opslog.info("已创建处理进程，线程ID: %s。开始压缩数据。" % str(p.pid))
    # 返回 内容
    return json({'app': local_ip, 'res': 'Received'})


if __name__ == "__main__":
    job = BackgroundScheduler()
    job.start()
    # 标记是否写入文件
    zipfile_ok = False
    # 写入私钥
    mypath = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(mypath + "/zipfile/"):
        os.makedirs(mypath + "/zipfile/")

    # 定时删除备份日志
    job.add_job(del_zipfile, 'cron', args=(7,), day='*', hour='01', minute='25')
    # 开启监听客户端监听
    app.run(host="0.0.0.0", port=10870, access_log=False)