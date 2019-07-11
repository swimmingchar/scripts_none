#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,os,time
import gzip

# 此程序解决解压并删除日志文件的功能
# 主要分两部分：
#    1. 解压文件，并将解压出来的文件写入日志；
#    2. 删除过期文件，文件过期时间可自定义

# 解压文件函数
def unzipfile(filepath):
    pass
# 删除过期日志文件函数
def dellogfile():
    pass

# 解析处理文件
def parsefile(inpath , outpath):
    # 读取可用文件列表
    inpath_list = list()
    # 读取需要删除的文件列表
    outpath_list = list()
    # 获取读取文件和删除文件目录下的文件列表
    for f in os.listdir(inpath):
        if os.path.isfile(inpath + '/' + f):
            inpath_list.append(f)

    for f in os.listdir(outpath):
        if os.path.isfile(outpath + '/' + f):
            outpath_list.append(f)

    # 排除目录
    # inpath_date_format = time.localtime(time.time())[3]
    # 假设文件处理完后移动至.bak/文件夹下
    for file in inpath_list:
        # app_name = file.split("_")[0]
        temp_list = file.split("-")
        f_m_path = file.split("-")[1] + '/' + file.split("_")[]

    

    

if __name__ == "__main__":
    in_path = out_path = None

    if len(sys.argv) != 2:
        print(" 脚本变量不足！请参照以下方式运行：")
        print(" none_unzip.py  --in_path=""  --out_path=""")
        sys.exit("参数不对！")
    elif len(sys.argv) == 2:
        if sys.argv[1].split("=")[0] == "--in_path": 
            in_path = sys.argv[1].split("=")[1]
        elif sys.argv[2].split("=")[0] == "--out_path":
            out_path = sys.argv[2].split("=")[1]
    
    if not in_path and not out_path:
        parsefile(inpath = in_path,  outpath = out_path)