#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import time
import datetime
import requests
import logging
from logging import handlers

from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import Process
from sanic import Sanic
# from sanic.exceptions import NotFound
from sanic.response import html, json, redirect
app = Sanic()

try:
    os.makedirs(os.path.dirname(os.path.realpath(__file__)) + '/logs/')
except Exception as msg:
    pass

# 日志logger初始化
opslog = logging.Logger('mserver')
fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                        datefmt='%Y%m%d %H:%M:%S,')

hd = handlers.TimedRotatingFileHandler('logs/mserver.log', when='midnight')
hd.setLevel(logging.INFO)
hd.setFormatter(fmt)
hd.suffix='%Y%m%d-%H%M%S'
opslog.addHandler(hd)

# 获取前一天时间
def Getyesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today-oneday
    return yesterday


# 定时收集日志
def crontbal_log(_applist):
    # TODO 获取应用列表(Redis方式，file方式)
    # 获取应用列表 使用ansible-host 方式读取列表

    # TODO FOR循环触发日志, backfile?pra_key=备份服务器key串&con_host=10.10.10.241&appname='remit-ore'&t_date=("2019",\
    #  "03",“01","12","20"), tran_date 为年月日时分元组
    # backfile?pra_key=备份服务器key串&con_host=10.10.10.241&appname='remit-ore'&t_date='20190303'&regx='2019.?03.?03'

    res_date = Getyesterday()
    # 转换成元组
    temp_date =  str(res_date.strftime('%Y')) + ',' + str(res_date.strftime('%m')) + ',' + str(res_date.strftime('%d'))

    tran_date = time.strftime("%Y%m%d%H%M", time.localtime())
    regx = '.*' + '.?'.join(temp_date.split(',')) + '.*'
    str_key = open(mypath + '/conf/key', 'r').readline()

    # 开始循环推送采集压缩文件通知
    for appname in _applist.keys():
        time.sleep(5)
        for appip in _applist[appname]:
            # j_data = {'appname': appname, 'clientip': appip, 'tran_date': tran_date, 'pra_key': keyfile}
            j_data = {'appname': appname, 'clientip': appip, 'date': tran_date, 'regx': regx, 'pra_key': str_key, 'con_host': '10.10.10.241'}
            url = 'http://' + appip + ':10870/backfile'
            try:
                url_get = requests.get(url, params=j_data, timeout=5)
                opslog.info("IP：%s 通知完成。返回信息：%s" % (appip, url_get.json()))
            except Exception as msg:
                opslog.info('应用:%s,IP地址:%s,日志备份推送错误,错误内容：\n%s' % (appname, str(appip), str(msg)))


# 写入记录
def wirtelogs(appname, clientip, file_name, res):
    w_file = str(time.strftime("%Y%m%d-%H%M%S", time.localtime())) + ".zlist"
    opslog.info("接收数据：应用名：%s;IP：%s;文件名：%s;传输状态：%s" % (appname, clientip, file_name, res))
    with open(mypath+ "/filelist/"+w_file,"a") as f:
        if res:
            f.writelines("%s:%s:%s" % (appname, clientip,file_name) + '\n')
    # opslog.info("应用：%s,客户端IP：%s录入完成。" % (appname, clientip))
    return()


@app.route("/zipinfo")
async def zipinfo(request):
    # opslog.info("Server Beginning. Port 10871 survival!")
    opslog.info("请求URL ： %s" % request.url)
    appname = request.args.get('appname')
    clientip = request.args.get('clientip')
    file_name = request.args.get('file_name')
    # file_size = request.args.get('file_size')
    res = request.args.get('REV')

    p = Process(target=wirtelogs, args=(appname, clientip, file_name, res))
    p.start()
    opslog.info("%s应用,接受到IP%s 请求，已创建处理线程，线程ID：%s" % (appname, clientip, str(p.pid)))
    return json({"query_string": request.query_string, 'res': 'Received'})


# 定时任务定时检查
def check_cront_job():
    opslog.info('定时任务列表：%s' % job.get_jobs())


# 根据ansible host 列表获取applist
def split_app():
    ansible_hosts = os.path.dirname(os.path.realpath(__file__)) + "/conf/hosts"
    with open(ansible_hosts, 'r') as f:
        # 初始化
        app_name = ""
        app_ip = list()

        for item in f.readlines():
            item = item.strip()
            if item.startswith('['):
                if len(app_ip) != 0:
                    app_list[app_name] = app_ip
                    app_ip = list()
                app_name = item[1:-1]
            elif item.startswith("10"):
                app_ip.append(item)
        app_list[app_name] = app_ip
    return app_list


# 需要在同级文件下手动创建conf文件夹，里面需要有ansible的hosts 文件和 key 文件，key文件为登陆备份服务器的公钥
if __name__ == "__main__":
    mypath = os.path.dirname(os.path.realpath(__file__))

    if not os.path.exists(mypath + "/filelist/"):
        os.makedirs(mypath + "/filelist/")

    # 初始化应用名和IP对照表
    app_list = dict()
    split_app()
    opslog.info("应用列表获取完成，内容如下：\n%s"%app_list)

    # 定时触发日志压缩传输
    job = BackgroundScheduler()
    # 定时日志触发
    job.add_job(crontbal_log, 'cron', args=(app_list,), day='*', hour='00', minute='25')
    # 每两个小时获取一次定时列表，确认定时任务状态
    job.add_job(check_cront_job, 'interval', hours = 2)
    job.start()

    # 启用服务端口监听
    app.run(host="0.0.0.0", port=10871, access_log=False)