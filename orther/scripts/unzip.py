#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys, zipfile, pickle, time
from datetime import datetime
from datetime import timedelta


# unzip_file 分为两种格式
# 1. 第一次用来检查压缩日志文件，格式如下：unzip_file(zip_file_list);
# 2. 第二中用法为第二次调用，用来解压zip文件，开头做了zip结尾限制。格式如下：unzip_file(zip文件全路径, 应用名);

def unzip_file(U_path="", app_name=""):
    # 解压文件
    if U_path.lower().endswith('zip'):
        u_file = zipfile.ZipFile(U_path,'r')

        try:
            u_file.extractall(path=unzip_path + app_name + "/")
            # 解压文件写入文件，待删除时使用
            with open(del_file_log + unzip_file_list ,'a') as f:
                for f_item in u_file.namelist():
                    f.writelines(unzip_path + app_name + "/" + f_item + "\n")

        except Exception as msg:
            print("%s 文件解压失败，解压目录为: %s，错误为: %s"%(U_path, unzip_path + app_name, msg))
            # TODO 发送邮件通知，通知解压失败

        finally:
            u_file.close
        # 删除&天之前的文件
        is_del_list_file = del_file_log + str(day_res.year) + str(day_res.month) + str(day_res.day) + ".list"

        if os.path.exists(is_del_list_file):
            with open(is_del_list_file, "r") as f:
                for f_item in f.readlines():
                    try:
                       if len(f_item.strip()) != 0:
                            os.system("rm -f f_item")
                    except Exception as msg:
                            print("%s 文件删除错误，错误为: %s"%(f_item,msg))

    # 读取解压汇总文件
    else:
        zip_after = dict([(f, None) for f in os.listdir(zip_file_list)])
        zip_new = [ f for f in zip_after if not f in zip_before ]

        # 更新初始字典列表写入pickle
        zip_before = zip_after
        with open(my_path + "/.config/zip_filelist", "w") as f:
            pickle.dump(zip_before, f)

        # 如果为空，则不进入for循环
        for item_file in zip_new:
            with open(item_file,"r") as f:
                for zip_file in f.readlines():
                    back_path = zip_file.split("_")[-1][:4] + "/" + zip_file.split("_")[-1][4:6] + "/" + zip_file.split("_")[0] + "/" + zip_file
                    print("需要解压文件名为：%s"%zip_file_path + back_path)
                    unzip_file(zip_file_path + back_path, zip_file.split("_")[0])



if __name__== "__main__":
    # 初始化变量
    # 收集文件路径
    my_path = os.path.dirname(os.path.realpath(__file__))

    zip_file_list = "/var/tmp/log_pack_list"
    zip_file_path = "/backup/typeback/Prod/"
    unzip_path = "/opt/catlogs/all/"
    del_file_log = my_path + "/.del_logs/"
    unzip_file_list = time.strftime("%Y%m%d",time.localtime(time.time())) + ".list"

    zip_before = dict([(f , None) for f in os.listdir(zip_file_list)])

    # 文件删除时间约定，默认为7天之前
    day_res = datetime.now() - timedelta(days=7)

    # 防止文件未创建
    if not os.path.exists(my_path + "/.config"):
        os.system("mkdir -p %s" % (my_path + "/.config"))

    if not os.path.exists(my_path + "/.log_bak"):
        os.system("mkdir -p %s" % (my_path + "/.log_bak"))
    #读取pickle
    with open(my_path + "/.config/zip_filelist", "r") as f:
        zip_before = pickle.load(f)    

    # 初始数据写入文件，防止重启丢失
    with open(my_path + "/.config/zip_filelist", "w") as f:
        pickle.dump(zip_before, f)

    # 调用解压,700秒调用一次，做一次目录对比
    while True:
        time.sleep(700)
        unzip_file(zip_file_list)

