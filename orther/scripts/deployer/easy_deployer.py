#!/usr/bin/env python
# coding:utf-8

import os
import sys
import time
import jenkins
import logging
from logging import handlers
import colored
from colored import stylize

deplog = logging.Logger('deploy')
fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                        datefmt='%Y%m%d %H:%M:%S,')
hd = handlers.TimedRotatingFileHandler('logs/easy_dep.log', when='midnight')
hd.setLevel(logging.INFO)
hd.setFormatter(fmt)
hd.suffix='%Y%m%d-%H%M%S'
deplog.addHandler(hd)


# 获取应用列表
def get_app():

    my_app = None
    app_ip = list()
    a_list = dict()
    with open(myapp_path + '/conf/hosts', 'r') as f:
        for item in f.readlines():
            if item.strip().startswith('['):
                if my_app is not None:
                    a_list[my_app] = app_ip
                    app_ip = list()
                my_app = item.strip()[1:-1]
            elif len(item.strip()) != 0:
                app_ip.append(item.strip())
        # 防止IP地址结尾和只有一个应用的情况
        if len(app_ip) == 0:
            deplog.info(stylize("配置文件结尾不是IP地址", colored.fg("226")))
        if len(app_ip) != 0:
            a_list[my_app] = app_ip
    return a_list


# 获取服务
def stats_jenkins():
    # jenkins admin token:   11b3f6d05fb4095465a3d2f7d17d5da3be
    server = jenkins.Jenkins('http://172.10.1.31:8080/', username='admin', password='admin')
    return server


# 部署应用
def deployer_ment(app_name):
    # 构建
    j_server = stats_jenkins()
    deplog.info(stylize('》》》》》开始部署 %s 应用《《《《《'% app_name,ok_color))
    print(stylize('》》》》》开始部署 %s 应用《《《《《'% app_name, right_color))
    for item in app_list[app_name]:
        param_dict = dict()
        param_dict['host'] = item
        build_number = j_server.get_job_info(app_name)['nextBuildNumber']
        input(stylize("==============》》》按回车键继续！《《《==============", right_color))
        try:
            j_server.build_job('account-core', parameters=param_dict)
            print(stylize("当前应用构建号为：%s" % str(build_number), right_color))
            cmd = stylize("%s 应用节点为：%s 开始部署，jenkins 部署号为：%s。" % (app_name, item, str(build_number))
                          , ok_color)
            deplog.info(cmd)
            print(cmd)
        except Exception as msg:
            cmd = stylize("%s 应用，构建节点为：%s 构建错误，错误内容为：%s。" % (app_name, str(item), msg)
                          , error_color)
            deplog.info(cmd)
            sys.exit(cmd)
        # build_status = j_server.get_build_info(app_name, int(build_number))['building']
        build_status = True
        start_time = int(time.time())
        print(stylize("正在构建中。。。。。请稍候。。。", ok_color))
        time.sleep(5)
        while build_status:
            # print("已经开始构建！")
            time.sleep(2)
            diff_time = int(time.time()) - start_time
            if diff_time % 4 == 0:
                print(stylize("%s 应用节点：%s 已部署%s秒。" % (app_name, item, str(diff_time)), ok_color))
            try:
                build_status = j_server.get_build_info(app_name, int(build_number))['building']
            except Exception:
                build_status = True
        # 获取构建输出
        res = j_server.get_build_console_output(app_name, build_number)
        # 输出到屏幕
        print(stylize("\n========> %s 应用节点 %s，部署完成，以下为构建日志：" % (app_name, item), right_color))
        res = res.split('\n')
        time.sleep(2)
        for i_out in res:
            print(i_out)
        print(stylize("日志输出完成。<===================================\n", right_color))
        if res[-2].endswith('SUCCESS'):
            deplog.info(stylize("%s 应用节点：%s 已成功部署。" % (app_name, item), ok_color))
        if not res[-2].endswith('SUCCESS'):
            deplog.info(stylize("%s 应用节点：%s 部署失败。" % (app_name, item), error_color))
            print(stylize("=======>节点部署失败，请检查！<======="), error_color)
    deplog.info(stylize("=======> %s 应用部署完成，包含节点如下：%s。<=======" % (app_name, app_list[app_name]),ok_color))


if __name__ == "__main__":
    # 读取应用IP
    myapp_path = os.path.dirname(os.path.realpath(__file__))
    error_color = colored.fg("1") + colored.attr("bold")
    right_color = colored.fg("82") + colored.attr("bold")
    ok_color = colored.fg("11") + colored.attr("bold")
    app_list = get_app()
    deplog.info(stylize("获取应用列表内容如下：%s" % app_list, colored.fg("196")))
    deployer_ment(sys.argv[1].lower())
    # deployer_ment("account-core")

