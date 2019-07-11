#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os,sys
try:
    from fabric2 import task, Connection,Executor
except:
    raise Exception("请安装fabric2")

try:
    import click
except:
    raise Exception("请安装click插件！")

#1、更换IP：主备机房
#2、更换以及添加Hostname
#3、替换zabbix-agent 配置为被动设置
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
def chanegip():


def changehostname():


def changezabbix():


if __name__ == '__main__':
    # version check
    if sys.version_info.major != 2 and sys.version_info.minor != 7:
        raise Exception('请使用Python2.7以上版本')
    
    if 
