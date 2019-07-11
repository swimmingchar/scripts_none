#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from email import utils
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import mimetypes, smtplib
import logs

## write logs (logfile:文件名，logmain：函数名, cmd：写入的内容)
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
        logs.loggin("xmail_logs","mail","read file is error , %s" % msg)

    try:
        message = MIMEMultipart()
        text = MIMEText(mail_data + "<div>" + additional + "</div>", 'html', "utf-8")
        message.attach(text)
        sender = "专线监控告警邮件"
    except Exception as identifier:
        logs.loggin("xmail_logs","mail", "Error is %s" % identifier)

    mail_to = to.split(",")
    # contentType = 'application/octet-stream'
    # mainType, subtype = contentType.split('/', 1)

    message['From'] = sender
    message['To'] = ",".join(mail_to)
    message['Subject'] = "%s" % (subject)
    message['Date'] = utils.formatdate()
    fulltext = message.as_string()
    server = smtplib.SMTP_SSL("test.cn", 465)
    password = "XXXXX"
    try:
        server.login('shiwm@test.cn', password)
    except Exception as msg:
        logs.loggin("xmail_logs", "mail", "The mail server is unarrived! The error is %s" % msg)

    try:
        server.sendmail(sender, mail_to, fulltext)
    except Exception as msg:
        logs.loggin("xmail_logs", "mail", "Send Mail Error：%s" % msg)
        server.quit()
    logs.loggin("xmail_logs", "mail", "The mail is send.")

# xmail.py 收件人【多个收件人使用,分割】 标题 内容 附加内容
if __name__=="__main__":
    if len(sys.argv) == 5:
        try:
            mail_send(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
            logs.loggin("xmail_logs", "mail", "send mail argv is to %s, subject %s, data is %s, adj is %s" % (sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
        except Exception as msg:
            logs.loggin("xmail_logs", "mail", "Send mail error, the msg is :%s" % msg)
            sys.exit(1)
        
    