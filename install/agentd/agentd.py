#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import psutil, platform, requests
import math
import json
import time
import schedule


def get_hostname():
    try:
        hostname = socket.getfqdn(socket.gethostname())
        ipaddr = socket.gethostbyname(hostname)
    except Exception as msg:
        print(msg)
        hostname = ''
        ipaddr = ''
    data = {'hostname': hostname, 'ipaddr': ipaddr, 'os': platform.platform()}
    return data


def get_cpu():
    logical = psutil.cpu_count()
    physical = psutil.cpu_count(logical=False)
    cpu_percent = psutil.cpu_percent(interval=1)
    data = {'logical': logical, 'physical': physical, 'cpu_percent': cpu_percent }
    return data


def get_memory():
    mem_info = psutil.virtual_memory()
    total = mem_info[0]/1024/1024/1024.0
    all_mem = math.ceil(total)
    percent = mem_info[2]
    data = {"total": all_mem, "percent": percent}
    return data


def get_disk():
    list1 = []
    for mount in psutil.disk_partitions():
        mount_point = mount[1]
        try:
            disk_usage = psutil.disk_usage(mount_point)[3]
        except Exception as msg:
            print(msg)
            disk_usage = ''
        data = {'mount_point': mount_point, 'disk_usage': disk_usage}
        list1.append(data)
    return list1


def data_info():
    data_info = {}
    data_info["hostname"] = get_hostname()
    data_info["cpu"] = get_cpu()
    data_info["memory"] = get_memory()
    data_info["disk"] = get_disk()
    return json.dumps(data_info)

#date = {"hostname": get_hostname(), "cpu": get_cpu(), "memory": get_memory(), "disk": get_disk()}

# def redis_save():

# if __name__ == '__main__':
#     while True:
#         redis_save(data_info()['hostname'],data_info())
#         print("redis save sccuessful!")
#         time.sleep(1)
def post_data():
    #data = {"hostname": get_hostname(), "cpu": get_cpu(), "memory": get_memory(), "disk": get_disk()}
    sys_data = data_info()
    print(sys_data)
    print("----------------++----------------")
    post_url = "http://10.10.0.24:8000/cmdb/collect/"
    try:
        res = requests.post(post_url, sys_data)
        print("The Post status code is :{0}".format(res.status_code))
    except Exception as identifier:
        print("Post Fail! ", identifier)

    print("-----------------------------------")


if __name__ == '__main__':
    schedule.every(10).seconds.do(post_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
