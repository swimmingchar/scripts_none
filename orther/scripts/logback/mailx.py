#!/usr/local/python37/bin/python3
# -*- coding:utf-8 -*-

import sys
from email import utils
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import mimetypes, smtplib
import logging
from logging import handlers

deplog = logging.Logger('xmail')
fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                        datefmt='%Y%m%d %H:%M:%S,')
hd = handlers.TimedRotatingFileHandler('/tmp/xmail.log', when='midnight')
hd.setLevel(logging.INFO)
hd.setFormatter(fmt)
hd.suffix='%Y%m%d-%H%M%S'
deplog.addHandler(hd)


if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

def mail_send(to, subject, data, additional):
    mail_data = ""
    try:
        with open(data, 'r') as f:
            for item in f.readlines():
                if item.strip() != '':
                    mail_data = mail_data + '<div>' + item.strip() + '</div>'
    except Exception as msg:
        deplog.info('read file is error , %s' % msg)

    message = MIMEMultipart()
    text = MIMEText(mail_data + "<div>" + additional + "</div>", 'html', "utf-8")
    message.attach(text)
    mail_to = to.split(",")
    contentType = 'application/octet-stream'
    mainType, subtype = contentType.split('/', 1)
    message['From'] = 'alert@elinkdata.cn'
    message['To'] = ",".join(mail_to)
    message['Subject'] = "%s" % (subject)
    message['Date'] = utils.formatdate()
    fulltext = message.as_string()
    server = smtplib.SMTP("smtp.mxhichina.com", 25)
    password = "DwyG4uenqA!PyHQwXUUgE"
    try:
        server.login('alert@elinkdata.cn', password)
    except Exception as msg:
        deplog.info(' The mail server is unarrived! The error is %s' % msg)

    try:
        server.ehlo()
        server.starttls()
        server.sendmail('alert@elinkdata.cn', mail_to, fulltext)
    except Exception as msg:
        deplog.info("Send Mail Error：%s" % msg)
        server.quit()
    deplog.info("The mail is send.")

# xmail.py 收件人【多个收件人使用,分割】 标题 内容 附加内容
if __name__=="__main__":
    if len(sys.argv) == 5:
        try:
            mail_send(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
            deplog.info("send mail argv is to %s, subject %s, data is %s, adj is %s" % (sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
        except Exception as msg:
            deplog.info("Send mail error, the msg is :%s" % msg)
            sys.exit(1)
    deplog.info("No Send Mail argv is %s" % sys.argv)
