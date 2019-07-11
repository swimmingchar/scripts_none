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

# 获取当前目录下switch文件夹内文件数量
switch_path = os.path.split(os.path.realpath(__file__))[0] + "/switch/"
# 如果没有status 文件夹则创建
status_path = os.path.split(os.path.realpath(__file__))[0] + "/status/"

# 当前时差计算
def time_diff(path, now):
    try:
        file_mtime = int(os.path.getmtime(path))
    except:
        logging.info("Error! The file %s is not in here!" % path)
        sys.exit('1')
    return int(now - file_mtime)

# 发送邮件
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
    server = smtplib.SMTP('mail.ul.com', 25)
    # 生产环境直接发送
    try:
        server.sendmail(sender, mail_to, fulltext)
        logging.info("The mail is send!")
    except Exception as msg:
        logging.info("Send Mail Error：%s" % msg)
        server.quit()

# 线路切换动作
def switch(room, line, status, host, send_to):
    # zline(专线名称或者动作，主备机房，状态)
    # 更具标签获取主备机房各自URL
    if room_sign == "master":
        line_url = "http://10.10.2.30:8888/gateway-payservice-core/controller/netStatus/notify"
        adj_room = '主机房'
    if room_sign == "slave":
        line_url = "http://10.10.20.30:8888/gateway-payservice-core/controller/netStatus/notify"
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
        # 当前目录下创建status/master or status/slave 文件
        if not os.path.exists(status_path):
            os.mkdir(status_path)
        # 情况状态文件目录内文件
        try:
            os.system('rm ' + status_path + '*')
        except Exception as msg:
            logging.info("Status Clean file is error %s" % msg)
        # 创建状态文件
        open(status_path + status, 'w').close()

        # 清空线路切换标识文件
        try:
            os.system('rm ' + switch_path + '*')
        except Exception as msg:
            logging.info("Switch Clean file is error %s" % msg)

        logging.info("line change success, the line is %s, back str is %s" % (status,url_back_str))
        if line == 'epcc':
            line = ',网联线路'
        if line == 'cup':
            line = ',银联线路'
        adj = adj_room + line + '，切换至 ' + status + '线路。'
        line_sendmail(send_to, "Line change report", adj , str(url_back_str))
    if not url_back_str.startswith("SUCCESS"):
        logging.info("The CURL ex failed!, back str is %s " % url_back_str )
        if line == 'epcc':
            line = ',网联线路'
        if line == 'cup':
            line = ',网联线路'
        adj = adj_room + line + '，切换至 ' + status + '线路。'
        # send mail url_back_str
        line_sendmail(send_to, "Line change report", adj, str(url_back_str))        

# 后期改进使用'Problem name'划分线路和恢复状态
if __name__ == "__main__":
    # 切换状态字典
    switch_item = dict()
    # 获取告警信息
    switch_send = dict()
    # 拆分告警内容
    msg_data = dict()

    os_out = os.popen("/sbin/ifconfig").read()
    try:
        re.search(r"10\.10\.16\.24", os_out).group(0)
        room_sign = "slave"
    except:
        room_sign = "master"

    # 将接受到的参数拆分合并至字典中
    for item in sys.argv:
        # 接收人
        if item.strip().startswith("--to="):
            switch_send["to"] = item.split("--to=")[1].strip()

        if item.strip().startswith("--subject="):
            switch_subject = item.split("--subject=")[1].strip()

        if item.strip().startswith("--message="):
            try:
                # 拆分 message 需要保证信息为“\r\n” 分割
                msg_split = item.split("--message=")[1].split('\r\n')
                # 需要默认有host，time，date
                for msg_item in msg_split:
                    if msg_item.strip() != '':
                        if msg_item.startswith("Problem started"):
                            msg_data["problem"] = msg_item
                            continue

                        # 添加依据Problem name 划分线路和状态
                        if msg_item.startswith('Problem name:'):
                            res_key = msg_item.split(":")[1].strip().split('_')[0]
                            res_value = msg_item.split(":")[1].strip().split('_')[1]
                            logging.info("Line Status  is %s _____________________ %s" % (res_key, res_value ) )
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
    # 线路区分关键参数
    switch_path = switch_path + switch_send["line"] + "/"
    status_path = status_path + switch_send["line"] + "/"

    switch_send["msg"] = msg_data
    logging.info("the switch_send is %s" % switch_send)
    # hostname_slave
    file_path = msg_data['host'] + '_' + switch_send["switch_status"]
    
    # 保证文件夹存在
    if not os.path.exists(switch_path):
        os.mkdir(switch_path)

    # 判断线路状态，如果切换状态文件存在，则表示已切换，退出，否则继续执行
    if os.path.exists(status_path + switch_send["switch_status"]):
        logging.info("This line was switched! This program is exited.")
        sys.exit('1')

    # 文件创建
    for root, dirs, files in os.walk(switch_path):
        # 是否超过60秒
        if time_diff(switch_path, int(time.time())) >= 60:
            # 清空文件删除文件
            try:
                os.system('rm ' + root + '*')
            except Exception as msg:
                logging.info("Error! The file %s @ is not removed! error is %s" % (files, msg))
            # 清空列表
            files = []
        # 如果存在，退出
        if file_path in files:
            logging.info("The line %s was switched. This program is exit." %  (switch_path + file_path))
            sys.exit('1') 
        # 如果没有创建文件，则创建文件
        if file_path not in files:
            # logging.info("OK")
            open(switch_path + file_path, 'w').close()
            files.append(file_path)
            logging.info("The files in switch is: %s" % files)
            logging.info("Files Num is %s" % len(files))
            if len(files) == 2:
                # 执行切换 (room, line, status, host)
                switch(room_sign, switch_send["line"], switch_send["switch_status"], msg_data["host"], switch_send["to"])
            else:
                logging.info("The root is %s, file len is %s" % (root,len(files)))
    logging.info("Complate!")
