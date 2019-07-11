#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pymongo
import time, json, datetime
import os, sys
import pickle, uniout, logging
# import logging2 as logging

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# 日志设置
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(levelname)s %(message)s',
                   datefmt='%Y%m%d %H:%M:%S',
                   filename='/tmp/get_mongodb.log',
                   encoding='utf-8',
                   filemode='ab+')

def get_alldata(col, get_datatime, mer_data):
    starttime = str((get_datatime + datetime.timedelta(seconds = -11)).strftime('%Y%m%d%H%M%S'))
    endtime = str((get_datatime + datetime.timedelta(seconds = -1)).strftime('%Y%m%d%H%M%S'))
    get_data = {}

    appname_pipeline = [{"$match": {"startTime": {"$gte": starttime,"$lt": endtime}}}, {"$group": {"_id": "$appName"}}]
    merid_pipeline = [{"$match": {"startTime": {"$gte": starttime,"$lt": endtime}}}, {"$group": {"_id": "$merId"}}]

    res_appname = list(col.aggregate(appname_pipeline))
    res_merid = list(col.aggregate(merid_pipeline))

    data = []
    for item in res_appname:
        data.append({"{#APP_NAME}": item['_id']})

    for item in res_merid:
        if item['_id'].strip() != "":
            mercid = str(item['_id'])
            
            try:
                data.append({"{#MERCID}": mercid})
                # merc = eval("u'"+mer_data[mercid]+"'")
                merc = mer_data[mercid]
                data.append({"{#MERC}": merc})
            except Exception as msg:
                logging.info("Get_all_data-Merc error. %s." %(msg))
                # print(msg)
    #print(data)
    get_data["data"] = data
    data_json = json.dumps(get_data, ensure_ascii=False)
    logging.info("The Mongodb Discovery Data is: %s" % data_json)
    return data_json

# 只查询应用访问次数
def get_data(col, get_datatime, moth, m_data, mer_data):
    starttime = str((get_datatime + datetime.timedelta(seconds = -2)).strftime('%Y%m%d%H%M%S'))
    endtime = str((get_datatime + datetime.timedelta(seconds = -1)).strftime('%Y%m%d%H%M%S'))
    merc_name = "NotinCode"

    # pipeline = [{"$match": {"startTime": {"$gte": starttime,"$lt": endtime},"appName":"merc-gateway-web"}}, {"$group": {"_id": moth, "total":{"$sum":1}}}]
    pipeline = [{"$match": {"startTime": {"$gte": starttime,"$lt": endtime}}}, {"$group": {"_id": moth, "total":{"$sum":1}}}]
    res = list(col.aggregate(pipeline))
    
    # 回传数据
    try:
        ack_num = str(res[0]['total'])
        logging.info("The %s ack_num is %s, Start Time is ---> %s" %(m_data, ack_num,str(starttime)))
        return ack_num
    except Exception as msg:
        logging.info("The %s Error is %s. Start Time is ---> %s" %(m_data, msg,str(starttime)))
        return 0
    # 商户号查询获取商户名
    #if moth == 'merId':
    #    try:
    #        merc_name = eval("u'"+mer_data[m_data]+"'")
    #        logging.info("商户名为:%s" % merc_name)
    #        # 推送商户名数据
    #        zabxsender = '/usr/local/zabbix3.2/bin/zabbix_sender'
    #        zabxserver = '10.10.10.24'
    #        hostname = 'Zabbix server'
    #        cmd = zabxsender + " -z " + zabxserver + " -p 10051 -s " + hostname + " -k " + "mer"+ merc_name + " -o " + ack_num + " -v &> /dev/null" 
    #        logging.info("zabbix sender command is: %s" % cmd)
    #        os.system(cmd)
    #    except Exception as msg:
    #        logging.info("The mercid is %s not in code.dict." %m_data)
    #        # print(msg)

def change_dict(file_path):
    j_data = dict()
    with open(file_path, 'rb') as f:
        for item in f.readlines():
            j_data[item.split('=')[0]] = item.split('=')[1].split('\r\n')[0]
        
    with open('code.dict', 'wb') as f:
        pickle.dump(j_data,f)


if __name__=="__main__":
    # get_datatime = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    get_datatime = datetime.datetime.now()

    # starttime = str(int(get_datatime) - 11)
    # endtime = str(int(get_datatime) - 1)
    
    conn = pymongo.MongoClient('10.10.2.145', 20000)
    db = conn.get_database('log')
    col_name = 'simpleLog'+ get_datatime.strftime('%Y%m%d%H%M%S')[:6]
    col = db.get_collection(col_name)
    
    # read mrec dict
    with open('code.dict','rb') as f:
        mer_data = pickle.loads(f.read())
    if len(sys.argv) == 1:
        # col 数据源， get_datatime 程序触发时间。mer_data 商户名和商户号对照字典
        print(get_alldata(col, get_datatime, mer_data))
    elif len(sys.argv) == 2:
        change_dict(sys.argv[1])
    elif len(sys.argv) == 3:
        # col 数据源； get_datatime 程序触发时间, sys.argv[1] 查询方法（商户号【merId】；应用名【appName】； sys.argv[2] 商户号或者商户名，mer_data 商户名和商户号对应字典）
        print(get_data(col, get_datatime, sys.argv[1], sys.argv[2], mer_data))