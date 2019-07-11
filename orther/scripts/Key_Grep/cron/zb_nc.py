#!/usr/bin/env python
# -*- coding:utf-8 -*-

import schedule, time, os, hashlib
import socket, sys

url_list_sum = ""
#参数说明
#url-list exmplod:
# www.allqr.cn:443:bns-jy:1
# www.allqr.cn:2322:bns-dz:60
# 144.112.33.229:8830:tjspd-jy:1
# 144.112.33.229:21:tjspd-dz:60
# trade.internetpaymentbanks.com:443:jcbank-jy:1
# bill.internetpaymentbanks.com:8522:jcbank-dz:60
# zjnrzj.95516.com:443:zjupay-jy:1
# 9.234.51.101:20125:shcup-jy:1
# 9.234.151.101:20125:bjcup-jy:1
# 9.234.1.31:22:cup-dz:60
# gateway.95516.com:443:cup-gateway:1
# vip.7shengqian.com:443:ydbank-jy:1

getfiletime = 0

def check_url_list():
    # 获取文件时间
    global getfiletime
    newfiletime = int(os.path.getmtime(os.getcwd()+"/../conf/url-list"))
    if getfiletime == 0:
        getfiletime = newfiletime
    if getfiletime != newfiletime:
        sys.exit(1) 

def bash_exec(cmdlist):
    #os.popen("sh zabix_sender.sh www.baidu.com 444 baidu-443 10.10.9.20 ")
    cmd = 'sh ../bin/zabix_sender.sh ' + ' '.join(cmdlist)
    os.popen(cmd) 

if __name__ == "__main__":

    # get ip
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    if myname.upper().startswith("BJ1"):
        zab_servip = '10.10.10.24'
        if '10.10.2' in myaddr:
            zab_servip = '10.10.2.117'

    if myname.upper().startswith("BJ2"):
        zab_servip = '10.10.16.24'

    check_url_list()
    with open(os.getcwd()+'/../conf/url-list', 'rb+') as f:
        for urline in f.readlines():
            if not urline.startswith("#"):
                res = urline.split(":")
                bash_args = (res[0] + " " + res[1] + " " + res[2] + " " + myaddr).split(" ")
                schedule.every(int(res[3])).seconds.do(bash_exec,bash_args)

    # 检查通道记录文件
    schedule.every(5).seconds.do(check_url_list)

    while True:
        schedule.run_pending()
        time.sleep(1)
