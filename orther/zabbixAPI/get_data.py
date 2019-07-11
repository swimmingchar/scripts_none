#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pyzabbix import ZabbixAPI
import json, xlrd, sys, platform
import configparser as cf


def read_conf(conf_path):
    cf_list = dict()
    config = cf.RawConfigParser()
    with open(conf_path, 'r') as cfgfile:
        config.readfp(cfgfile)
        cf_list['user'] = config.get('zabbix', 'user')
        cf_list['password'] = config.get('zabbix', 'passwd')
    print('Config data is:', cf_list)
    return cf_list


def read_xl(xl_path):
    xlrd.open_workbook(xl_path)
    data = []
    with xlrd.open_workbook(xl_path) as xl_book:
        sheet = xl_book.sheet_by_index(0)
        print("excel row is {0}\nexcel col is {1}".format(sheet.nrows, sheet.ncols))
        for ros in range(1, sheet.nrows):
            d1 = {}
            for cos in range(sheet.ncols):
                d_key = sheet.cell(0, cos).value
                d_vul = sheet.cell(ros, cos).value
                if d_key == "port":
                    d_vul = int(d_vul)

                d1[d_key] = d_vul
            data.append(d1)
    return data


def get_zhost_data(zpath, zurl, zhlist):
    conf_file = read_conf(zpath)

    z = ZabbixAPI(zurl)
    z_user = conf_file['user']
    z_passwd = conf_file['password']
    z.login(user=z_user, password=z_passwd)
    print(z.host.get())
    print("+++++++++Begin get zabbix data!+++++++++")
    data_list = {}
    date = {}
    # get hostid
    for zabbix_ip in zhlist:
        res = z.host.get(filter={"host": zabbix_ip})
        # print("This is :", res[0]['hostid'].encode('utf-8'))
        try:
            if res[0]['hostid']:
                # data_list['ip'] = zabbix_ip
                date['hostid'] = res[0]['hostid'].encode('utf-8')
                data_list[zabbix_ip] = date
        except IndexError:
            continue
    print("*********-------********")
    print(data_list)
    
    # get cpu max && 7 days
    # res = z.item.get(filter={"hostid": 10256})
    res = z.item.get({
        "output": "extend",
        "hostid": 10256,
        "search":{
            "key_": "proc"
        }
    })

    print("***************************************")
    # with open('path.txt', "w") as pfile:
    #     pfile.write(str(res))
    print("***************************************")
    z_host_list=z.host.get(filter={"host": "10.10.16.200"})
    print(z_host_list[0]['hostid'],z_host_list[0]['name'])
    # print("-----&&&&-------Item is:", res)
    # get mem less && 7 days
    # with open('path.txt', "w") as pfile:
    #     pfile.write(str(res))

    # get network uesd

    # get disk use

    return True


if __name__ == '__main__':
    # cpath = input("input sysconf path: ")
    # cpath = "C:\\Import\\system.conf"
    # xl_path = "C:\\Import\\python-test\\test01\\python-test\\zabbix-host.xls"
    # change os
    if platform.platform().startswith("Windows"):
        excel_host_path = ".\\cmsops\\zhoubao-test.xls"
        system_path = ".\\system.conf"
        xl_path = ".\\z-host-list.xls"
        z_url = "http://172.10.1.31/zabbix"
    else:
        excel_host_path = "../../zhoubao-test.xls"
        system_path = "../../system.conf"
        xl_path = "../../z-host-list.xls"
        z_url = "http://10.10.0.21/zabbix"

    # print(z.api_version())
    # z_host = read_xl(xl_path)
    # print(z.host.get())
    # print(z_host)
    # print("====================+++++======================")
    # for item_host in z_host:
    #     print("host is:", item_host["host"])
    #     print("host is:", item_host["name"])
    #     print("host is:", item_host["description"])
    #     print("host is:", item_host["template"])
    #     print("host is:", item_host["group"])
    #     print("host is:", item_host["ip"])
    #     print("host is:", item_host["port"])
    #     print("^%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%^")

    z_ip_list = []
    with xlrd.open_workbook(excel_host_path) as xl_book:
        xl_sheet = xl_book.sheet_by_name("Sheet1")
        for col_item in range(1, xl_sheet.nrows):
            if xl_sheet.cell(col_item, 2).value:
                # print("this sheet cells is :", xl_sheet.cell(col_item, 2))
                z_ip_list.append(xl_sheet.cell(col_item, 2).value)
    print(z_ip_list)
    print('%%%%%%%%%%%%%%%%__----====get zabbix data start!====----__%%%%%%%%%%%%%%%')
    get_zhost_data(system_path, z_url, z_ip_list)

        # 添加主机组并返回groupsids
        # 添加主机组并返回
        # try:
        #     z.group.get({
        #         "output":"extend",
        #         "filter":{
        #             "host":[
        #                 "Zabbix server"
        #             ]
        #         }
        #     })
        # except Exception as msg:
        #     zgroup = z.hostgroup.create({
        #         "name": "meet"
        #     })
        #     print(zgroup['groupids'])
        # 获取模板ID
        # try:
        #     z_temp = z.template.get(filter={'name': 'Template OS Linux'})
        # except Exception as identifier:
        #     print('template is error:', identifier)
        # print(z_temp)
        # 返回查找的主机ID
        # z_host_list=z.host.get(filter={"host": "172.10.1.38"})
        # print(z_host_list)
        # 创建主机组
        # try:
        #     z_group = z.hostgroup.create({
        #         "filter": {
        #             "name": item_host["host"]
        #         }})
        # except Exception as e:
        #     print("group is exit!")
        #     sys.exit(1)
        # z.host.create({
        #     "host": item_host["host"],
        #     "interfaces": [{
        #         "type": 1,
        #         "main": 1,
        #         "useip": 1,
        #         "ip":  item_host["ip"],
        #         "port": item_host["port"]
        #     }],
        #     "groups": [{
        #         "groupid": "0"
        #     }],
        #     "templates": [{
        #         "templateid": "0"
        #     }],
        #     "inventory_mode": 0
        # })


