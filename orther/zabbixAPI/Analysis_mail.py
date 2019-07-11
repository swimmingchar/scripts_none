#!/usr/bin/env python
# -*- coding:utf-8 -*-

import poplib
import email
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from datetime import datetime

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def guess_charset(msg):
    # 先从msg对象获取编码:
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，再从Content-Type字段获取:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

def print_info(msg, indent=0):
    if indent == 0:
        # 邮件的From, To, Subject存在于根对象上:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    # 需要解码Subject字符串:
                    value = decode_str(value)
                else:
                    # 需要解码Email地址:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        # 如果邮件对象是一个MIMEMultipart,
        # get_payload()返回list，包含所有的子对象:
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % ('  ' * indent, n))
            print('%s--------------------' % ('  ' * indent))
            # 递归打印每一个子对象:
            print_info(part, indent + 1)
    else:
        # 邮件对象不是一个MIMEMultipart,
        # 就根据content_type判断:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            # 纯文本或HTML内容:
            content = msg.get_payload(decode=True)
            # 要检测文本编码:
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % ('  ' * indent, content + '...'))
        else:
            # 不是文本,作为附件处理:
            print('%sAttachment: %s' % ('  ' * indent, content_type))


if __name__ == "__main__":
    email = "shiwm@test.com"
    password = "xxxxxxxxx"
    pop3_server = "pop3.test.com"

    server = poplib.POP3_SSL(pop3_server)
    # server.set_debuglevel(1)

    print(server.getwelcome().decode('utf-8'))

    server.user(email)
    server.pass_(password)

    print("Mail counts: %s, Storage Size: %s"% (server.stat()[0],  server.stat()[1]))

    res, mails, octets = server.list()
    index = len(mails)
    print(index)
    resp, lines, octets = server.retr(index-1)
    msg_content = '\n'.join(lines)
    # print(msg_content)
    msg = Parser().parsestr(msg_content)
    date = msg.get('date')
    print("邮件接收时间为： %s" % date)
    atime = datetime.strptime(date[:-5], "%a, %d %b %Y %H:%M:%S ")
    print(atime)
    # print_info(msg)
    msgs = msg[globalsMai]

    server.quit()




# import poplib
# import email
# from email.parser import Parser
# from email.header import decode_header
# from email.utils import parseaddr


# passwd = "test"
# user = "shiwm@test.com"
# s = poplib.POP3_SSL('pop3.test.com')
# s.user(user)
# s.pass_(passwd)
# res, mails, octets = s.list()

# index = len(mails)

# resp, lines, octets = s.retr(index-1)
# msg_content = '\n'.join(lines)

# msg = Parser().parsestr(msg_content)

# atime = msg.get('date', '')

# date = datetime.strptime(atime[:-5], '%a, %d %b %Y %H:%M:%S ')


# a = enumerate(msg.get_payload())

# with open('mail.txt', "w") as f:
#     for i in mails:
#         f.write(i)
#         f.write('\n')