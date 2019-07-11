#!/usr/bin/env python
# -*- coding:utf-8 -*-

#获取关键字并使用zabbix_sender推送。


import os, subprocess, time
import sys
import schedule

reload(sys)
# sys.path.append(os.getcwd() + "\\..\\sbin\\")
# sys.path.append(os.getcwd() + "/../sbin/")

# from get_process import log

file_list=["/home/tomcat/app/logs/catalina.out",
           "/home/tomcat/app/logs/platform.log",
           "/home/tomcat/app/logs/info.log",
           "/home/tomcat/app/logs/error.log"]

def grep_key(str_key):
    with open(os.getcwd() + "/../temp/", "rb") as f:
        errlog_str = f.readline()

    file_signle = ""

    for logfile in file_list:
        cmd = "grep -B2 "+ str_key + " " + logfile + " | tail -2 |head -1 | awk '{print $1\" \"$2}'" 
        res_str = os.popen(cmd).readline()
        # 如果没有返回值，泽继续下一个
        if len(res_str) < 1:
            continue
        # 拆分时间
        err_log_time = res_str.eplit(".")[0]
        if "." in  res_str:
            err_log_time = res_str.split(".")[0]
        elif "\n" in res_str:
            err_log_time = res_str.split("\n")[0]
        # 尝试时间分片
        try:
            new_log_time = int(time.mktime(time.strptime(err_log_time, "%y-%m-%d %H:%M:%S")))
        except Exception as msg:
            # write logs (logfile:文件名，logmain：函数名, cmd：写入的内容)
            # log("get_"+str_key, "get_key", msg)
            return 0 

        if int(errlog_str) < int(new_log_time):
            errlog_str = new_log_time
            file_signle = logfile

    if file_signle == "":
        


    
           

if __name__=="__main__":
    str_key = "MyBatisSystemException"

    schedule.every(3).minutes.do(grep_key,str_key)

    while True:
         schedule.run_pending()
         time.sleep(1)