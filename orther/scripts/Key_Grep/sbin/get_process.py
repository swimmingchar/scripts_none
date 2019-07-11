#!/usr/bin/env python
# -*- coding:utf-8 -*-

#每隔N秒zabbix触发，探测进程是否存在，不存在则重新启动后。
import os, time, socket, datetime, sys
import psutil

try:
    import psutil
except:
    os.system("pip install ./packages/psutil-5.4.7.tar.gz")
    import psutil

#发送进程监控消息至zabbix_server服务器
def send(itemdata):
    # zab_sender_path = os.popen('which zabbix_sender').read().split('\n')[0]
    zab_sender_path = "/usr/bin/zabbix_sender"
    
    #使用自带sender，只适用于redhat6
    # if not os.path.exists(zab_sender_path):
        # zab_sender_path = "../bin/zabbix_sender"

    #get localhost ip
    myaddr = socket.getfqdn(socket.gethostname())
    myip = socket.gethostbyname(myaddr)

    if myaddr.split("-")[0] == "BJ1":
        zab_server = "10.10.10.24"
        if myip.split(".")[2] == 2 or myip.split(".")[2] == 5 :
            zab_server = "10.10.2.117"

    if myaddr.split("-")[0] == "BJ2":
        zab_server = "10.10.130.135"

    #zabbix agent key on sennder
    zab_key= "get_key"
    
    #send data
    cmd = zab_sender_path + " -z " + zab_server + " -p 10051 -s " + myip + " -K " + zab_key + " -o " + itemdata
    os.system(cmd)
    log("zabx_sender","sender",cmd)

#查看 process 传递过来的进程cmdline是否存在，1：存在；0：：不存在
def get_processing(process):
    res = psutil.process_iter()
    # psutil.Process('40949').cmdline()
    for item in res:
        # schedule.every(1).seconds
        if process in item.cmdline():
            log("process","get_process",item.cmdline())
            return 1
    return 0

#重启get_key进程
def start_get_key(check_pname):
    # logdate = time.strftime("%F %T", time.localtime(time.time()))
    cmd = "python " + check_pname
    os.system(cmd)
    log("process","start_get_key",cmd)

# write logs (logfile:文件名，logmain：函数名, cmd：写入的内容)
def log(logfile,logmain,cmd):
    logdate = datetime.datetime.now().strftime('%Y%m%d')
    logtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    my_path = os.getcwd()
    log_path = my_path + "/../logs/" + logfile +"-" + logdate + ".log"
    line = logtime + " - " + logmain + ": " + cmd + "."
    with open(log_path , 'wb+') as f:
        f.writelines(line)

if __name__ == '__main__':
    try:
        pymain = sys.argv[1]
    except:
        sys.exit()

    cron_cmd = "../cron/"+ pymain
    if get_processing(cron_cmd) == 0:
        start_get_key(cron_cmd)