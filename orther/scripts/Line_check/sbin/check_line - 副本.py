#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 加载bin目录模块
import yaml
import os, re, time, json,sys
import requests
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from email import utils
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import mimetypes, smtplib


if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
# 日志功能 write logs (logfile:文件名，logmain：函数名, cmd：写入的内容)
from lineMode import logs
# 邮件功能 mail_send(to, subject, data, additional)
from fabric2 import ThreadingGroup as hostgroup
from fabric2 import *

# 发送邮件，内容传递为数组（*args）
def line_sendmail(to, subject, adj = None, *args):
    mail_data = "<div>&nbsp;</div>"
    for item in args:
        mail_data = mail_data.strip() + "<div>" + item.strip() + "</div>"
    logs.loggin("check_line","SENDMAIL","Mail data is %s" % mail_data)
    message = MIMEMultipart()
    text = MIMEText(mail_data + "<div>" + adj + "</div>", 'html', "utf-8")
    message.attach(text)
    sender = "Alert"
    mail_to = to.split(",")
    message['From'] = sender
    message['To'] = ",".join(mail_to)
    message['Subject'] = "%s" % (subject)
    message['Date'] = utils.formatdate()
    fulltext = message.as_string()
    # 测试环境
    server = smtplib.SMTP_SSL("test.cn", 465)
    password = "xxxxxxxx"
    try:
        server.login('shiwm@test.cn', password)
    except Exception as msg:
        logs.loggin("check_line","SENDMAIL",' The mail server is unarrived! The error is %s' % msg)
    # 发送功能
    # 生产环境直接发送
    try:
        server.sendmail(sender, mail_to, fulltext)
        logs.loggin("check_line","SENDMAIL","The Mail is Send!")
    except Exception as msg:
        logs.loggin("check_line","SNEDMAIL","Send Mail Error: %s"% msg)
        server.quit()

# 定时任务
def do_check(**zip_dict):
    global line_time
    get_res = dict()
    global room_sign
     # 故障时首次处理
    line_singe = zip_dict["singe"]+"_"+ str(zip_dict["name"])
    # 命令执行成功返回1 ，失败返回 0
    cmd = "nc -vz -w 1 " + str(zip_dict["ip"]) + "  " + str(zip_dict["port"]) + " && echo 1 || echo fail"
    try:
        # 备机房
        # pool = Group("tomcat@10.10.222.16","tomcat@10.10.222.18","tomcat@10.10.222.136","tomcat@10.10.222.137","tomcat@10.10.222.166","tomcat@10.10.222.167").run(cmd, hide=True)
        # 主机房
        # pool = Group("tomcat@10.10.208.16","tomcat@10.10.209.16", "tomcat@10.10.209.136","tomcat@10.10.209.137", "tomcat@10.10.209.166", "tomcat@10.10.209.167")
        res = pool.run(cmd,hide=True)
        
    except Exception as msg:
        logs.loggin("check_line","DO_CHECK","Fabric2 group exxor. "% msg)
    # 获取结果  ip:resulaiat
    for ihost in pool.values():
        get_res[ihost.connection.host] = ihost.stdout.strip()
    logs.loggin("check_line","CHECK","%s 线路NC探测返回数据 : %s" %(line_singe,get_res))

    # 如果返回值没有1，则线路故障，开始告警
    if "succeed" not in ",".join(str(i) for i in get_res.values()):
        # print(get_res.values())
        if int(line_time[line_singe +"_downtime"]) == 0:
            line_time[line_singe +"_downtime"] = int(time.time())
            #互斥
            line_time[line_singe +"_uptime"] = 0
            logs.loggin("check_line","MSG","%s 下线时间%d"%(line_singe,zip_dict["downtime"]))
        elif int(line_time[line_singe + "_downtime"]) != 0:
            dif_time = int(time.time()) - int(line_time[line_singe + "_downtime"])
            logs.loggin("check_line","MSG","%s FAIL_time_dif %d"%(line_singe,int(dif_time)))
            # print("Lineis %s, is %s" % (line_singe, line_time[line_singe + "_status"]))
            if dif_time  >=  int(zip_dict["downtime"]):
                # 超出告警允许时间
                logs.loggin("check_line","CHECK","line_singe_status not -eq 0")
                if line_time[line_singe + "_status"] != 0:
                    logs.loggin("check_line","CHECK"," 故障时间大于阈值%d"%(zip_dict["downtime"]))
                    # 线路在可用列表
                    if zip_dict["name"] in ",".join(str(i) for i in get_list(payagte=zip_dict["singe"]).values()):
                        # print("故障2")
                        # 执行下线动作
                        res = get_list(payagte=zip_dict["singe"],status="disconnect",line=zip_dict["name"])
                        # 记录日志
                        logs.loggin("check_line","DO_CHECK","URL推送返回结果 %s"%res)
                        # 发送邮件,1800秒内，每300秒发送一次邮件
                        mail_start_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                        mail_end_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()+1800))
                        scheduler.add_job(line_sendmail,'interval',args=[send_to, "线路故障", "%s线路下线。" % zip_dict["singe"]+"_"+zip_dict['name']],minutes=5,start_date=mail_start_time,end_date=mail_end_time)
                        # line_sendmail(send_to, "线路故障", "%s线路下线。" % zip_dict["singe"]+"_"+zip_dict['name'])
                        s_title = "主机房"
                        if room_sign == "Slave":
                            s_title = "备机房"
                        logs.loggin("check_line","MAIL","%s %s 线路下线。通知开始时间%s，结束时间%s" %(s_title, zip_dict["text"] + "_" + str(zip_dict['name']),str(mail_start_time),str(mail_end_time)))
                        # 变更时间
                        line_time[line_singe + "_downtime"] = 0 
                        line_time[line_singe + "_status"] = 0

    # 恢复处理
    if "fail" not in ",".join(str(i) for i in get_res.values()):
        # print("%s-------%d" %(line_singe,line_time[line_singe + "_uptime"])
        # 恢复首次处理
        if int(line_time[line_singe + "_uptime"]) == 0:
            line_time[line_singe + "_uptime"] = int(time.time())
            # 互斥
            line_time[line_singe + "_downtime" ] = 0
            # 记录故障状态
            logs.loggin("check_line","REV","%s 线路预计%d 秒后恢复." %(line_singe,zip_dict["uptime"]))
        elif int(line_time[line_singe + "_uptime"]) != 0:
            # print("OK!")
            dif_time = int(time.time()) - int(line_time[line_singe + "_uptime"])
            logs.loggin("check_line","MSG","%s SCCU_time_dif %d"%(line_singe,int(dif_time)))
            # 超出告警允许时间
            if dif_time >= int(zip_dict["uptime"]):
                logs.loggin("check_line","CHECK"," 恢复时间大于阈值 %d"%(zip_dict["uptime"]))
                if line_time[line_singe + "_status"] != 1:
                    # 线路在可用列表
                    # print("恢复进度")
                    if zip_dict["name"] not in ",".join(str(i) for i in get_list(payagte=zip_dict["singe"]).values()):
                        # print("恢复2")
                        # 执行恢复操作
                        res = get_list(payagte=zip_dict["singe"],status="connect",line=zip_dict["name"])
                        # 记录日志
                        logs.loggin("check_line","DO_CHECK","URL推送返回结果 %s"%res)
                        # 恢复邮件只发送一次
                        logs.loggin("check_line","MAIL","%s 线路已在线。" % zip_dict["text"]+"_"+str(zip_dict['name']))
                        # 邮件通知
                        s_title = "主机房"
                        if room_sign == "Slave":
                            s_title = "备机房"
                        line_sendmail(send_to, s_title + "线路恢复告警！", s_title + " %s 线路恢复请知悉!")
                        # 初始化时间和标识
                        line_time[line_singe + "_uptime"] = 0
                        line_time[line_singe + "_status"] = 1



# 检查线路定时生成模块
def check_line(lines,line_info):
    zip_dict = dict()
    for line in lines:
        zip_dict["ip"]      = line_info[line]["ip"]   
        zip_dict["port"]    = line_info[line]["port"]
        zip_dict["host"]    = line_info[line]["checkpoint"]
        zip_dict["singe"]   = line_info[line]["singe"]    #epcc
        zip_dict["name"]    = str(line)          #BJ01
        zip_dict["uptime"]  = line_info[line]["uptime"]
        zip_dict["downtime"]= line_info[line]["downtime"]
        if zip_dict['singe'] == "epcc":
            zip_dict['text'] = "网联"
        elif zip_dict['singe'] == "cup":
            zip_dict['text'] = "银联"
        logs.loggin("check_line","CHECK_LINE",str(zip_dict))
        # 添加 线路监控任务
        scheduler.add_job(do_check,'interval', kwargs=zip_dict,seconds=line_info[line]["acktime"],id=zip_dict['singe']+ "_" + str(line))
        logs.loggin("check_line","ADD_JOB","%s【任务ID】线路定时任务添加完成.时间间隔为%s秒。"%(zip_dict['text']+ "_" + str(line),line_info[line]["acktime"]))
        if scheduler.get_job(job_id=zip_dict['singe']) is None:
            # 添加获取线路可用列表，5分钟一次
             scheduler.add_job(get_list,'interval', args = [zip_dict['singe'],], minutes = 5, id = zip_dict['singe'])
             logs.loggin("check_line","ADD_JOB","%s【任务ID】可用线路探测任务添加完成.时间间隔为5分钟。" %zip_dict['text'])
        logs.loggin("check_line","JOB",str(scheduler.get_jobs()))

    while True:
        time.sleep(1)

# url 推送，获取列表，发送故障恢复功能
def get_list(payagte,status = "detect",line = None):
    global send_to
    global url
    global url_get

    if line is None:
        line_data = {'payagte': payagte, 'operate': status}
    else:
        line_data = {'payagte': payagte, 'operate': status, 'line': line}
    
    logs.loggin("check_line","GET_LIST","探测url 为：%s, 携带数据是: %s" %(url,line_data))

    try:
        url_get = requests.get(url, params=line_data, timeout=2)
    except Exception as msg:
        logs.loggin("check_line","GET_LIST","%s可用线路获取失败。 %s" %(payagte,msg))

    try:
        # 参数line为None的时候，返回json
        logs.loggin("check_line","GET_LIST","%s 获取可用线路 %s" %(payagte,url_get.json()))
        return url_get.json()
    except Exception as msg:
        # 参数Line不是None的时候，返回字符串
        url_back_str = url_get.text.encode('utf-8').split('\n')[0]
        logs.loggin("check_line","GET_LIST","%s 线路推送返回值：%s" %(payagte,url_back_str))
        # xmail.mail_send(send_to, "Line switch back str is %s" %url_back_str)
        return url_back_str


if __name__ == "__main__":
    # 初始化定时
    scheduler = BackgroundScheduler()
    scheduler.start()
    # 机房判断
    os_out = os.popen("/sbin/ifconfig").read()
    try:
        # re.search(r"10\.10\.16\.24", os_out).group(0)
        re.search(r"10\.10\.16\.23", os_out).group(0)
        room_sign = "Slave"
        url = "http://x.x.x.x:8888/gateway-payservice-core/controller/line/status/notify"
    except:
        room_sign = "Master"
        url = "http://x.x.x.x:8888/gateway-payservice-core/controller/line/status/notify"
    # for linux
    yamlconf=os.path.dirname(os.path.realpath(__file__)) + "/../conf/line.yaml"
    # 读取配置文件
    try:
        yamlf = open(yamlconf,'r')
        yaml_data = yaml.load(yamlf)
    except Exception as msg:
        logs.loggin("check_line","YAML", str(msg))
        line_sendmail(send_to,"专线监控脚本异常告警！","读取YAML配置异常,%s" % msg, room_sign+"机房。")
    logs.loggin("check_line","CONFIG", str(yaml_data))
    # 告警邮件
    send_to = yaml_data["altermail"]
    # 获取专线线路标识列表
    LineN = yaml_data["LineNo"][room_sign]
    # 获取机房线路信息字典
    allLine = yaml_data[room_sign]
    logs.loggin("check_line", "GET LINES", "lines is %s" % LineN )
    logs.loggin("lines_info ", "GET LINES", "line info is %s" % allLine)
    # 初始化 故障或者恢复时间标签
    line_time= dict()
    for item in LineN:
        line_time[allLine[item]['singe']+"_"+ str(item) + "_uptime"] = 0
        # 模式成功线路
        line_time[allLine[item]['singe']+"_"+ str(item) + "_status"] = allLine[item]['status']
        # line_time[allLine[item]['singe']+"_"+ str(item) + "_status"] = 1
        line_time[allLine[item]['singe']+"_"+ str(item) + "_downtime"] = 0
    # 调用专线探测模块
    check_line(LineN, allLine)
