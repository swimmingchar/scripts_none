#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import time
import datetime
import fabric2
import logging
from logging import handlers
import yaml


# 日志logger初始化
opslog = logging.Logger('deployer')
fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                        datefmt='%Y%m%d %H:%M:%S,')
hd = handlers.TimedRotatingFileHandler('logs/deployer.log', when='midnight')
hd.setLevel(logging.INFO)
hd.setFormatter(fmt)
hd.suffix='%Y%m%d-%H%M%S'
opslog.addHandler(hd)


#TODO get svn repo with url

#TODO maven  /opt/apache-maven-3.6.0/bin/mvn  clean package -Pqa  -Dmaven.test.skip=true  -Dmaven.compile.fork=true

#TODO deployer with host



# 部署应用
def deployment_app(app_name):
    pass


# 应用回滚
def rollback_app(app_name):
    pass


# 回显发布历史
def echo_display_history(app_name):
    # 需要对比，保证两个版本都一样的才可以显示
    pass


# 写入回显版本历史
def write_hist_ver(app_name):
    # 远程版本会写本地yml文件
    pass


# 获取svnpath
def get_svn(app_name):
    pass


# mavn 打包
def py_maven(app_name):
    # 首先过滤POM内的 "-SNAPSHOT"

    # mvn clean package -Pproc -Dmaven.test.skip=true -U -X
    pass








#程序入口
# 回滚：deployer.py [rollback] bwf-in
# 发布：deployer.py bwf-in

if __name__ == "__main__":
    myapp_path = os.path.dirname(os.path.realpath(__file__))

    # 读取应用配置
    _yml = open(myapp_path + '/hosts.yml', encoding='utf-8')
    host_yml = yaml.load(_yml)
    opslog.info("YAML配置文件读取内容为：%s" % host_yml )

    if len(sys.argv) == 2:
        # 发布
        deployment_app(sys.argv[1])
        pass
    if len(sys.argv) == 3:
        # 回滚
        rollback_app(sys.argv[2])
        pass
