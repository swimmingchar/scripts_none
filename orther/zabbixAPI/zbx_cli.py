#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import argparse

# 导入zabbix_tool.py的zabbix_api类                                                                                                                             
from zbx_tool import zabbix_api  

reload(sys)
sys.setdefaultencoding('utf-8')

host_file = 'target'
base_templates = "'aaa',"
cmd = 'python zbx_tool.py'

# 实例化zabbix_api                                                                                                                                                                   
zabbix=zabbix_api()  

def create_hosts():
    groups = raw_input("Please Input Group Name: ")
    add_templates = raw_input("Please Input Template Name: ")
    templates = base_templates + add_templates
    cmd1 = cmd + ' -A ' + groups
    os.system(cmd1)

    with open(host_file) as fb:
        host_info = dict(line.strip().split(',') for line in fb)

    for hostname in host_info:
        cmd2 = cmd + ' -C ' + host_info[hostname] + ' ' + groups + ' ' +templates + ' ' + hostname
        os.system(cmd2)

# 如果本机是sat，target文件可以只写主机名，然后用salt获取ip,上一段脚本如下修改：
#    with open(host_file) as fb:
#        host_info = list(line.strip() for line in fb)
#
#    for hostname in host_info:
#        ip_cmd='salt ' + hostname + ' grains.item fqdn_ip4|xargs'
#        ip = os.popen(ip_cmd).read().split()[4]
#        cmd2 = cmd + ' -C ' + ip + ' ' + groups + ' ' +templates + ' ' + hostname
#        os.system(cmd2)

def get_hosts(): 
   with open(host_file) as fb:                                                                                                                                  
       [zabbix.host_get(line.strip()) for line in fb] 

def delete_hosts():
   with open(host_file) as fb:
       [zabbix.host_delete(line.strip()) for line in fb] 

def enable_hosts():
   with open(host_file) as fb:
       [zabbix.host_enablee(line.strip()) for line in fb] 

def disable_hosts():
   with open(host_file) as fb:
       [zabbix.host_disable(line.strip()) for line in fb] 

def get_groups():
   with open(host_file) as fb:
       [zabbix.host_create()]

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == '-h':
        print("you need a argv,like:")
        print("""
        python zbx_cli.py -A #批量添加主机
        python zbx_cli.py -C #批量查询主机
        python zbx_cli.py -D #批量删除主机
        python zbx_cli.py -e #批量开启主机
        python zbx_cli.py -d #批量禁止主机
        python zbx_cli.py -getgroup #批量获取主机组
        """)
    else:
        if sys.argv[1] == '-A':
            create_hosts()
        elif sys.argv[1] == '-C':
            get_hosts()
        elif sys.argv[1] == '-D':
            delete_hosts()
        elif sys.argv[1] == '-e':
            disable_hosts()
        elif sys.argv[1] == '-d':
            enable_hosts()
        elif sys.argv[1] == '-getgroup':
            get_groups()