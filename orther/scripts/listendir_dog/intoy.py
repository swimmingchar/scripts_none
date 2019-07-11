#!/usr/bin/env python
# -*- coding:utf-8 -*-

<<<<<<< HEAD
import os,sys,time,datetime
import configparser
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import subprocess

# 重写类
class MyHandler(LoggingEventHandler):

    def on_moved(self, event):
        if not event.is_directory:
            if check_file(event.src_path):
                res= time.ctime() + ":  Moved file is: " +  event.src_path + "; To: " + event.dest_path
                print(res)
                log("watch_dog", "moved", res)
                rsync_file()
                print("Watach dir is %s" %watch_dog["monitor_path"])

    def on_created(self, event):
        if not event.is_directory:
            if check_file(event.src_path):
                res = time.ctime() + ":  Created file is: " + event.src_path 
                print(res)
                log("watch_dog", "create", res)
                rsync_file()
                print("Watach dir is %s" %watch_dog["monitor_path"])

    def on_modified(self, event):
        if not event.is_directory:
            if check_file(event.src_path):
                res = time.ctime() + ":  Modified file is: " + event.src_path
                print(res)
                log("watch_dog", "modified", res)
                rsync_file()
                print("Watach dir is %s" %watch_dog["monitor_path"])


# 检查文件是否为临时文件
def check_file(c_file):
    if sys.platform.upper().startswith("W"):
        file_name = c_file.split("\\")[-1]
    if sys.platform.upper().startswith("L"):
        file_name = c_file.split("/")[-1]

    if file_name.startswith("."):
        return False
    else:
        return True


def log(logfile,logmain,cmd):
    logdate = datetime.datetime.now().strftime('%Y%m%d')
    logtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    my_path = os.getcwd()
    
    # linux 平台
    if sys.platform.upper().startswith("L"):
        log_path = my_path + "/../logs/" 
    # Winodws 平台
    if sys.platform.upper().startswith("W"):
        log_path = my_path + "\\logs\\" 
    # 日志文件全路径
    logall_path = log_path + logfile +"-" + logdate + ".log"
    # 判断路径是否存在
    try:
        if not os.path.exists(log_path):
            os.mkdir(log_path)
    except Exception as msg:
        print("文件路径错误: %s" % msg)
        sys.exit()

    line = logtime + " - " + logmain + ": " + str(cmd) + ";"
    # 写入日志
    with open(logall_path , 'a') as f:
        f.writelines(line + '\n')


# 文件同步
def rsync_file():
    global check_time
    global rsync_conf
    # 保证不会多个进程在同步
    if int(time.time()) - check_time < 20:
        
    check_time= int(time.time())
    myEnv = dict(os.environ)
    mypath = os.getcwd()
    myEnv["rsync_path"] = rsync_conf["sbin"]
    if ',' in rsync_conf["dst_ip"]:
        for ip in rsync_conf["dst_ip"]:
            rsync_cmd = ".\\rsync.exe -rztlPD --chmod=ugo=rwX --exclude=\".[!.]*\" " + rsync_conf["src"] + " " + rsync_conf["user"] + "@" + ip + "::" + rsync_conf["deamon"] + " --password-file=" + rsync_conf["pwd"]
            # 执行命令写入日志
            log("rsync", "command", rsync_cmd)
            # 获取执行命令返回结果
            os.chdir(rsync_conf['sbin'])
            res = subprocess.Popen(rsync_cmd, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,env=myEnv)
            os.chdir(mypath)
            stdout = res.stdout.readlines()
            for i in stdout:
                print(str(i,encodeing = "utf-8"))
            log("rsync","Process",stdout)
    if ',' not in rsync_conf["dst_ip"]:
        rsync_cmd = ".\\rsync.exe -rztlPD --chmod=ugo=rwX --exclude=\".[!.]*\" " + rsync_conf["src"] + " " + rsync_conf["user"] + "@" + rsync_conf["dst_ip"] + "::" + rsync_conf["deamon"] + " --password-file=" + rsync_conf["pwd"]
        # rsync_cmd = '\"' + str(rsync_conf["sbin"]) + '\"'  + " -azvP --progress " + rsync_conf["src"] + " " + rsync_conf["user"] + "@" + rsync_conf["dst_ip"] + "::" + rsync_conf["deamon"] + " --password-file=" + rsync_conf["pwd"]
        log("rsync", "command", rsync_cmd)
        # 获取执行命令返回结果
        os.chdir(rsync_conf["sbin"])
        print("The Path is : %s" % os.getcwd())
        res = subprocess.Popen(rsync_cmd, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,env=myEnv)
        os.chdir(mypath)
        stdout = res.stdout.readlines()
        for i in stdout:
            print(str(i,encodeing = "utf-8"))
        log("rsync","Process",stdout)


# .\rsync.exe -avzP --progress /cygdrive/c/vrv test@172.10.1.121::test --password-file=/cygdrive/c/password.txt


if __name__ == '__main__':
    # 申请两个字典存放配置文件变量
    watch_dog = dict()
    rsync_conf = dict()
    # 记录执行时间
    check_time = int(time.time())

    if sys.platform.startswith('w') and sys.version.startswith('3'):
        if len(sys.argv) != 1 :
            parser = configparser.ConfigParser()
            file_path = os.path.dirname(os.path.realpath(__file__)) + '\\config'
            print("The Path is: %s" % file_path)
=======
import os,sys
import configparser


watch_dog = dir()
rsync_conf = dir()

if __name__ == '__main__':
    if sys.platform.startswith('w'):
        if len(sys.argv) == 1 :
            parser = configparser.ConfigParser()
            file_path = os.path.dirname(os.path.realpath(__file__)) + '\\config'
>>>>>>> af92289ee4a9dfeefa3d72b8327f45354513843b
            parser.read(file_path)
            for section in parser.sections():
                if section.startswith('watch'):
                    for item in parser.items(section):
                        watch_dog[item[0]] = item[1]
                if section.startswith('rsync'):
                    for item in parser.items(section):
<<<<<<< HEAD
                        rsync_conf[item[0]] = item[1]
        else:
            print("缺少参数，使用方式如下：python inoty.py .")
            sys.exit()

        log("watch_dog","conf",watch_dog)
        log("watch_dog","conf",rsync_conf)

    print("The List is: %s\n%s" %(watch_dog, rsync_conf))

    event_handler = MyHandler()
    observ = Observer()
    if not len(watch_dog['monitor_path']):
        sys.exit("No! Path!")
    else:
        print('watch dir is %s'% watch_dog['monitor_path'])
    
    observ.schedule(event_handler, path=watch_dog['monitor_path'], recursive=True)
    observ.start()
=======
                        rsysnc_conf[item[0]] = item[1]



from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import configparser2 as config 



def listendog():
    path = "c:\Import\help\"
    event_handler = LoggingEventHandler()
    observer = Observer
    observer.schedule(event_handler, path, recursize=True) 
    observer.start()
>>>>>>> af92289ee4a9dfeefa3d72b8327f45354513843b
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
<<<<<<< HEAD
        observ.stop()
    observ.join()
=======
        observer.stop()
    observer.join()


>>>>>>> af92289ee4a9dfeefa3d72b8327f45354513843b
