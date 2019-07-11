#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging, paramiko
from fabric2 import task, Connection, Executor
import schedule, time

import os, sys
from stat import S_ISDIR, ST_MODE

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# LOG_FILE = '/tmp/get_filename.log'
LOG_FILE = 'C:\\Import\\get_filename.log'

# 日志格式化
logging.handlers.RotatingFileHandler(LOG_FILE, mode='a', maxBytes=100*1024*1024, backupCount=2)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    # filename=LOG_FILE,
                    encoding='utf-8',
                    filemode='ab+')

# 删除存放文件的文件夹
def del_file(file_path):
    c = Connection('localhost')
    with c.cd("/home/tomcat/shiwm-service/"):
        res = c.run('[ -d %s ] && echo 00 || echo 11' % file_path, hide=True).stdout
        logging.info("The res is %s" %res)
        if res.startswith("00"):
            c.run("rm -rf ./sftp-duizhang/")
            logging.info("The die is exits， delete it now.")
            c.run("mkdir -p sftp-duizhang")
            logging.info("The die isn't exits， mkdir it now.")
        else:
            c.run("mkdir -p sftp-duizhang")
            logging.info("The die isn't exits， mkdir it now.")

# 遍历文件
def get_file_list(sftp, remote_dir):
    local_path = "/home/tomcat/shiwm-service/sftp-duizhang"
    if remote_dir[-1]=="/":
        remote_dir = remote_dir[0:-1]
    file = sftp.listdir_attr(remote_dir)
    for item in file:
        filename = remote_dir + '/' + item.filename

        if S_ISDIR(item.st_mode):
            b = filename.split("/")
            logging.info("The dir is： %s。The filename is %s" % (filename,b[1]))
            get_file_list(sftp, filename)
        else:
            if len(remote_dir) != 0:
                with open(local_path + '/' +  remote_dir.split("/")[1], "a+") as f:
                    logging.info("the filename is %s" % filename)
                    f.seek(0)
                    f.write("ChangeTime:%s    AccessTime:%s    " %(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.st_mtime)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.st_atime))))
                    f.write(filename + '\n')
def rsyn_file():
    passwd_file = "/home/tomcat/shiwm-service/py-scripts/get_sftp_list/scripts/rsync.pwd"
    rsync_bin = "/usr/bin/rsync"
    source_dir = "/home/tomcat/shiwm-service/sftp-duizhang"
    c = Connection("127.0.0.1")
    res = c.run(" %s -azvP %s --password-file=%s tomcat@x.x.x.x::sftp-duizhang" % (rsync_bin, source_dir, passwd_file))
    logging.info("Rsync message: %s" % res.stdout)

# 定时，循环拉取文件
def job():

    logging.info("------------Start------------")
    logging.info("The schedule BIGEN!")
    # SFTP连接初始化
    trans = paramiko.Transport((ip, int(port)))
    trans.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(trans)

    # 定义循环开始位置
    remote_dir="/"
    # 检查存放文件目录并清空
    del_file("sftp-duizhang")
    # 调用循环函数
    get_file_list(sftp, remote_dir)
    logging.info("-------------Rsync---------")
    rsyn_file()
    logging.info("------------END------------")


if __name__=="__main__":
    ip = '172.10.1.122'
    port = 13579
    user = "hfbank"
    passwd = "123.com"

    # schedule.every().hour.do(job)
    schedule.every(10).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)