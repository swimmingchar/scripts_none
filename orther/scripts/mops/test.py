#!/usr/bin/env python3
# coding:utf-8
#
# import paramiko
#
# host='10.10.10.241'
# p_user='tomcat'
# p_passwd='1qaz@WSX3edc'
# local_path = '/tmp/1.tar.gz'
# remove_path = '/tmp/1.gz'
# local_path.strip()
#
# trans = paramiko.Transport(host, 22)
# trans.connect(username=p_user, password=p_passwd)
# sftp = paramiko.SFTPClient.from_transport(trans)
# sftp.put(local_path,remove_path)
# print("传输完成。")
import logging
import time
from logging import handlers
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess

ops = logging.Logger('ops')
fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                        datefmt='%Y%m%d %H:%M:%S,%p')

hd = handlers.TimedRotatingFileHandler('ops.log', when='S',interval=5)
hd.setLevel(logging.INFO)
hd.setFormatter(fmt)
hd.suffix='%Y%m%d-%H%M%S'
ops.addHandler(hd)


def start_job():
    ops.info("计时时间是%s" % (str(time.ctime())))
    cmd = "find /zipfile -type f -mtime +1| xargs rm -f"
    # obj = subprocess.run(["find", "/tmp","-type", "f","-mtime","+1"], stdout=subprocess.PIPE)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for i in p.stdout.readlines():
        i = str(i.decode(encoding='utf-8')).split('\n')[0]
        ops.info("结果为%s" % i)
    for i in p.stderr.readlines():
        i = i.decode(encoding='utf-8').split('\n')[0]
        ops.error("错误内容为%s" % i)


def get_job():
    ops.info("任务列表为%s" % job.get_jobs())


if __name__ == '__main__':
    job = BackgroundScheduler()
    job.add_job(start_job,'interval', seconds = 10)
    # job.add_job(get_job,'interval', seconds = 200)
    job.start()
    ops.info("任务启动成功:%s" % job.get_jobs())
    while True:
        time.sleep(1)
