#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, os
import datetime,time


# write logs (logfile:文件名，logmain：函数名, cmd：写入的内容)
def loggin(logfile,logmain,cmd):
    logdate = datetime.datetime.now().strftime('%Y%m%d')
    logtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    my_path = os.path.dirname(os.path.realpath(__file__))

    # for windows 
#     log_path = my_path + "\\..\\..\\logs\\" + logfile +"-" + logdate + ".log"
    # for linux
    log_path = my_path + "/../../logs/" + logfile +"-" + logdate + ".log"
#     print(log_path)
    line = logtime + " - " + logmain + ": " + cmd + "."
    with open(log_path , 'a') as f:
        f.writelines(line)
        f.writelines("\n")

if __name__ == '__main__':
    loggin("meet","command","test")
    # print(os.path.dirname(os.path.realpath(__file__)))
