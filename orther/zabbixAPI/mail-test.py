#!/usr/bin/python
#coding:utf-8

from email import utils
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import mimetypes, smtplib
import os.path  
import sys

recipient = "swm108321@163.com"
sender = "shiwm@xxxxx.com"
message =  MIMEMultipart()

subject = "%s" % ("subject")
body = "body"
text = MIMEText(body, 'html')
text.set_charset('utf-8')
message.attach(text) 

contentType = 'application/octet-stream'  
mainType,subtype = contentType.split('/', 1)  

message['From'] = sender
message['To'] = recipient
message['Subject'] = subject
message['Date'] = utils.formatdate()  
fullText = message.as_string( )  
server = smtplib.SMTP_SSL("smtp.xxxx.com", 465)
password = "xxxxx"
server.login(sender, password)
try:  
    server.sendmail(sender, recipient, fullText)  
finally:  
    server.quit()  
print('Send OK')