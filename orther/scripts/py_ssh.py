#!/usr/bin/env python
# -*- coding:utf-8 -*-

import paramiko, threading, logging
import sys
from fabric.api import env, run,hides
from fabric.colors import *

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# 日志格式化
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename='/tmp/ssh_connect.log',
                    encoding='utf-8',
                    filemode='ab+')
try:
    import ConfigParser
except Exception as msg:
    logging.info("Import Error %s " % msg)


# 入口
if __name__=="__main__":


@parallel(pool_size=2)
def cmd_grep(g_host):
    with settings(warn_only=True):
        #with hide('aborts','status','running', 'stdout'):
            with cd('/home/tomcat/app/webapps'):
                res = run('grep -rw '+g_host+' *')
    re_res = res.spli('\n')
    if res.strip() != '':
        print green("Find res:%s" %g_host)
        if len(re_res) > 1:
            for item in re_res:
                print yellow("The host is:\n%s, \nthe res is:\n/home/tomcat/app/webapps/%s \n" % (env.host, item))
        else:
            print yellow("The host is:\n%s, \nthe res is:\n/home/tomcat/app/webapps/%s \n" % (env.host, res))
        
    else:
        print red("Warning message: '"+env.host+"' is no this str '"+g_host+"'.\n")

def local_cmd():
    local('ls')