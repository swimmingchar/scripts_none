#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys, os, re, time
from email import utils
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import mimetypes, smtplib

try:
    import requests, logging
except Exception as msg:
    logging.info("Import Error! %s" % msg)

# import redis

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# 日志格式化
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename='/tmp/change_line.log',
                    encoding='utf-8',
                    filemode='ab+')

# 定义线路切换状态文件路径为当前目录下的switch文件内
switch_path = os.path.split(os.path.realpath(__file__))[0] + "/switch/"
# 定义线路状态标识文件路径为当前目录下的status文件内
status_path = os.path.split(os.path.realpath(__file__))[0] + "/status/"

# 计算文件夹修改时间和当前时间时间差，返回值
def time_diff(path, now):
    try:
        file_mtime = int(os.path.getmtime(path))
    except:
        logging.info("Error! The file %s is not in here!" % path)
        sys.exit('1')
    return int(now - file_mtime)

# 发送邮件，内容传递为数组（*args）
def line_sendmail(to, subject, adj, *args):
    mail_data = "<div>&nbsp;</div>"
    for item in args:
        mail_data = mail_data.strip() + "<div>" + item.strip() + "</div>"
    logging.info("Mail data is %s" % mail_data)
    message = MIMEMultipart()
    text = MIMEText(mail_data + "<div>" + adj + "</div>", 'html', "utf-8")
    message.attach(text)
    sender = "SwitchlineNotice"
    mail_to = to.split(",")
    message['From'] = sender
    message['To'] = ",".join(mail_to)
    message['Subject'] = "%s" % (subject)
    message['Date'] = utils.formatdate()
    fulltext = message.as_string()
    # 生产环境
    # server = smtplib.SMTP('test.com', 25)
    # 测试环境
    server = smtplib.SMTP_SSL("test.com", 465)
    password = "xxxxxxxxxx"
    try:
        server.login('shiwm@test.com', password)
    except Exception as msg:
        logging.info(' The mail server is unarrived! The error is %s' % msg)
    # 发送功能
    try:
        server.sendmail(sender, mail_to, fulltext)
        logging.info("The mail is send!")
    except Exception as msg:
        logging.info("Send Mail Error：%s" % msg)
        server.quit()

# 线路切换动作
def switch(room, line, status, send_to):
    # 根据标签获取主备机房各自URL
    if room_sign == "master":
        line_url = "http://x.x.x.x:8888/gateway-payservice-core/controller/netStatus/notify"
        adj_room = '主机房'
    if room_sign == "slave":
        line_url = "http://x.x.x.x:8888/gateway-payservice-core/controller/netStatus/notify"
        adj_room = '备机房'
    # 获取json {'engineRoom':"master", 'payagte': "epcc", 'line': "master"}
    line_data = {'engineRoom':room, 'payagte': line, 'line': status}

    # 执行切换操作,超时时间需要实际计算
    try:
        # logging.info("Start Time is %s" % time.time())
        url_get = requests.get(line_url, params=line_data, timeout=2)
        # logging.info("End Time is %s" % time.time())
    except Exception as msg:
        logging.info("Line switch is error %s" % msg)
        line_sendmail(send_to, "Line switch is error", "by python for " + room, str(msg.args[0]))
        sys.exit('1')

    # 获取返回值
    url_back_str = url_get.text.encode('utf-8').split('\n')[0]
    logging.info("HTTP bank code is: %s, bank data is %s" % (url_get.status_code, str(url_back_str)))

    # 判断是否执行成功
    if url_back_str.startswith("SUCCESS"):
        # 因为要写入文件，因此如果文件夹不存在，创建文件夹
        if not os.path.exists(status_path):
            os.mkdir(status_path)
        # 清空线路状态标识文件
        try:
            os.system('rm ' + status_path + '*')
        except Exception as msg:
            logging.info("Status Clean file is error %s" % msg)
        # 创建线路状态文件
        open(status_path + status, 'w').close()

        # 清空线路切换标识文件
        try:
            os.system('rm ' + switch_path + '*')
        except Exception as msg:
            logging.info("Switch Clean file is error %s" % msg)

        logging.info("line change success, the line is %s, back str is %s" % (status,url_back_str))
        if line == 'epcc':
            line = ',网联线路'
        adj = adj_room + line + '，切换至 ' + status + '线路。'
        # 发送邮件
        line_sendmail(send_to, "Line change report", adj , str(url_back_str))
    # 返回值不是以seccess开头，处理方法
    if not url_back_str.startswith("SUCCESS"):
        logging.info("The CURL ex failed!, back str is %s " % url_back_str )
        if line == 'epcc':
            line = ',网联线路'
        adj = adj_room + line + '，切换至 ' + status + '线路。'
        # 携带返回值发送邮件
        line_sendmail(send_to, "Line change report", adj, str(url_back_str))


# change_line.py
if __name__ == "__main__":
    # 存放告警信息
    switch_send = dict()
    # 存放告警内容
    msg_data = dict()
    # 更具zabbixIP,判断是所在机房
    os_out = os.popen("/sbin/ifconfig").read()
    try:
        re.search(r"10\.10\.16\.24", os_out).group(0)
        room_sign = "slave"
    except:
        room_sign = "master"

    # 将接受到的参数拆分合并至switch_send
    for item in sys.argv:
        # 接收人
        if item.strip().startswith("--to="):
            switch_send["to"] = item.split("--to=")[1].strip()
        # 告警标题
        if item.strip().startswith("--subject="):
            switch_subject = item.split("--subject=")[1].strip()
        # 告警内容
        if item.strip().startswith("--message="):
            try:
                # 拆分 message 需要保证信息为“\r\n” 分割
                msg_split = item.split("--message=")[1].split('\r\n')
                # 需要默认有host/Problem name:
                for msg_item in msg_split:
                    if msg_item.strip() != '':
                        if msg_item.startswith("Problem started"):
                            msg_data["problem"] = msg_item
                            continue

                        # 添加依据Problem name 划分线路和状态
                        if msg_item.startswith('Problem name:'):
                            res_key = msg_item.split(":")[1].strip().split('_')[0]
                            res_value = msg_item.split(":")[1].strip().split('_')[1]
                            logging.info("Line Status is %s _____________________ %s" % (res_key, res_value ) )
                            switch_send["line"] = res_key
                            if res_value == 'problem':
                                switch_send["switch_status"] = "slave"
                            elif res_value == 'recovery':
                                switch_send["switch_status"] = "master"
                            continue

                        msg_data[msg_item.split(":")[0].strip().lower()] = msg_item.split(":")[1].strip()

                        logging.info("msg data is %s, value is %s" % (msg_item.split(":")[0], msg_item.split(":")[1]))
            except Exception as msg:
                logging.info("Split error : %s ; the msg data is %s" % (msg, item.split("--message=")[1]))
                sys.exit('1')
    switch_send["msg"] = msg_data
    logging.info("the switch_send is %s" % switch_send)
    # 拼接线路切换标识文件名
    file_path = msg_data['host'] + '_' + switch_send["switch_status"]
    
    # 因为需要写入文件，因此保证线路切换状态文件夹[switch]存在
    if not os.path.exists(switch_path):
        os.mkdir(switch_path)

    # 判断线路状态，如果切换状态文件存在，则表示已切换，退出，否则继续执行
    if os.path.exists(status_path + switch_send["switch_status"]):
        logging.info("This line was switched! This program is exited.")
        sys.exit('1')

    # 获取文件，文件夹信息
    for root, dirs, files in os.walk(switch_path):
        # 判断switch文件夹修改时间和当前时间是否超过60秒
        if time_diff(switch_path, int(time.time())) >= 60:
            # 清空switch文件夹
            try:
                os.system('rm ' + root + '*')
            except Exception as msg:
                logging.info("Error! The file %s @ is not removed! error is %s" % (files, msg))
            # 清空文件列表
            files = []
        # 如果线路切换文件存在，退出
        if file_path in files:
            logging.info("The line %s was switched. This program is exit." %  (switch_path + file_path))
            sys.exit('1') 
        # 如果线路切换文件不存在，则创建文件，后续处理
        if file_path not in files:
            # 创建标识文件
            open(switch_path + file_path, 'w').close()
            # 添加列表
            files.append(file_path)
            logging.info("The files in switch is: %s" % files)
            logging.info("Files Num is %s" % len(files))
            # 如果达到要求，执行切换脚本
            if len(files) == 2:
                # 执行切换switvh(机房标识，线路标识，切换至线路，通知人)
                switch(room_sign, switch_send["line"], switch_send["switch_status"], switch_send["to"])
            else:
                logging.info("The root is %s, file len is %s" % (root,len(files)))
    logging.info("Complate!")