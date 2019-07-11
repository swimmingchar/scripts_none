#!/usr/bin/env python
# -*- coding:utf-8 -*-

import schedule, logging, requests
from email import utils
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import mimetypes, smtplib
import sys, os, time, re

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# 日志格式化
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename='/tmp/line_corn.log',
                    encoding='utf-8',
                    filemode='ab+')
# 机房标识
room_sign = "a"

# 邮件发送
def line_sendmail(to, subject, data, adj):
    mail_data = "<div>&nbsp;</div>"
    mail_data = mail_data + "<div>" + data.strip() + "</div>"
    message = MIMEMultipart()
    text = MIMEText(mail_data + "<div>" + adj + "</div>", 'html', "utf-8")
    message.attach(text)
    sender = "Notice"
    mail_to = to.split(",")
    message['From'] = sender
    message['To'] = ",".join(mail_to)
    message['Subject'] = "%s" % (subject)
    message['Date'] = utils.formatdate()
    fulltext = message.as_string()
    server = smtplib.SMTP('test.com', 25)
    # try:
    #     server.login('shiwm@test.com', password)
    # except Exception as msg:
    #     logging.info(' The mail server is unarrived! The error is %s' % msg)
    try:
        server.sendmail(sender, mail_to, fulltext)
        logging.info("邮件已发送! ")
    except Exception as msg:
        logging.info("Send Mail Error：%s" % msg)
        server.quit()

# 线路状态检测
def line_status():
    line_s = os.path.split(os.path.realpath(__file__))[0] + "/status/slave"
    if os.path.exists(line_s):
        if room_sign == 'master':
            data = "主机房网联线路处于备用线路，请注意。\n"
        if room_sign == 'slave':
            data = "备机房网联线路处于备用线路，请注意。\n"
        line_sendmail("shiwm@test.com", room_sign  + " Line in slave.", str(data) ,"From cron.py")
        logging.info("Notice! %s 机房 %s "% (room_sign , data))

# API端口检测
def check_api():
    if room_sign.lower() == "master":
        ipaddr = "x.x.x.x:8888"
    if room_sign.lower() == "slave":
        ipaddr = "x.x.x.x:8888"
    url = "http://" + ipaddr + "/gateway-payservice-core/controller/netStatus/notify"
    epcc_line_data = {'engineRoom':room_sign , 'payagte': 'epcc', 'line': 'detect'}
    cup_line_data = {'engineRoom':room_sign , 'payagte': 'cup', 'line': 'detect'}
    logging.info("URL is %s ,data is %s" % (url, epcc_line_data))
    logging.info("URL is %s ,data is %s" % (url, cup_line_data))
    # 执行脚本epcc
    try:
        logging.info("Start Time is %s" % time.time())
        url_get = requests.get(url, params=epcc_line_data, timeout=2)
        logging.info("End Time is %s" % time.time())
    except Exception as msg:
        logging.info("Line change is error %s" % msg)
        #退出后可保证获取不到地址后正常运行
        # sys.exit(1)
        return 0

    try:
        logging.info("Start Time is %s" % time.time())
        url_get = requests.get(url, params=cup_line_data, timeout=2)
        logging.info("End Time is %s" % time.time())
    except Exception as msg:
        logging.info("Line change is error %s" % msg)
        #退出后可保证获取不到地址后正常运行
        # sys.exit(1)
        return 0

    

    # 获取返回值
    url_back_str = url_get.text.encode('utf-8').split('\n')[0]
    if url_back_str.strip().lower() != 'r':
        line_sendmail("shiwm@test.com", room_sign  + " is gateway-payservice-core api port is error!", str(url_back_str) ,"From cron.py")
        logging.info("Error! http back msg is %s" % url_back_str)
    logging.info("URL Back is %s " % url_back_str )

# 后台执行即可
if __name__=="__main__":
    os_out = os.popen("/sbin/ifconfig").read()
    try:
        re.search(r"10\.10\.16\.24", os_out).group(0)
        room_sign = "slave"
    except:
        room_sign = "master"
    logging.info("Room is %s" % room_sign)
    # 线路状态
    schedule.every(5).minutes.do(line_status)
    # api状态
    schedule.every(1).minutes.do(check_api)

    while True: 
        schedule.run_pending()
        time.sleep(1)