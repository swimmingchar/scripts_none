#!/usr/bin/env python
# -*- coding:utf-8 -*-

import imaplib, string, email
import sys, datetime, time, re
from email.header import decode_header
from email.utils import parseaddr
import xdrlib, pickle, os, platform

reload(sys)
sys.setdefaultencoding('utf-8')
if platform.platform().startswith('Windows'):
    list_path = 'pro_list\\'
else:
    list_path = 'pro_list/'
if not  os.path.exists(list_path):
    os.mkdir(list_path)
# p_line = {
#   'pro':'PJ20180934',
#   'work': '个人组',
#   'data': "天津浦发代付通道生产参数配置",
#   'puser':"吴晓宇",
#   'opreation':"上线申请",
#   'opdata':"2018-06-23 12:24",            #申请时间
#   'approval_time':"2018-06-23 13:43",     #操作时间
#   'slave_time':"2018-06-23 14:33",        #备机房完成时间
#   'master_time':"2018-06-23 15:33",       #主机房操作时间
#   'operator':"张国辉",                     #执行人
#   'checker':"邹国平",                      #验收人
#   'checktime':"2018-06-23 20:20"          #验收时间
#   'Time':"time"                           邮件时间
# }

p_line = {
  'pro':' ',
  'work': ' ',
  'data': " ",
  'puser':" ",
  'opreation':" ",
  'opdata':' ',                        #申请时间
  'approval_time':' ',                 #操作时间
  'slave_time': '',                    #备机房完成时间
  'master_time':' ',                   #主机房操作时间
  'operator':" ",                      #执行人
  'checker':" ",                       #验收人
  'checktime':' ',                     #验收时间
  'time':0                             #邮件时间
}

user = "shiwm@test.com"
paswd = ""
imap_server = "imap.xxxx.com"
dev_group = ['个人组','运维部','基础支付开发组','商户组','资金组','风控组','业务平台组', '技术架构组']
subject_group = ['数据变更','上线申请','安全变更','网络变更','配置变更','数据提取','生产访问','设备变更','密钥申请','数据销毁','其他变更']

s = imaplib.IMAP4_SSL(imap_server, 993)
s.login(user, paswd)
alist = s.list()[1]
# 私有处理，其他邮箱可能会报错
try:
    alist.remove('() "/" "xxxxxxx"')
except:
    sys.exit("邮箱【监控告警】目录没有")

for itme in alist:
    lpath, apath, rpath = itme.split(" ")
    s.select(mailbox=rpath)
    atype, date = s.search(None, 'ALL')
    # res = date[0].split(" ")
    print '\n'
    print "++++++++++Start+++++++++"
    print "DIR is :",itme
    sdate = date[0].split()
    if len(sdate) == 0:
        continue
    if len(sdate) != 0:
        print "共有封邮件：", len(sdate)
    for mail_list in reversed(sdate):
        try:
            etype, data = s.fetch(mail_list, '(RFC822)')
        except Exception as msg:
            print("Fetch is ", mail_list)
            continue

        try:
            s_msg = email.message_from_string(data[0][1].decode('utf-8'))
        except Exception as msg:
            print('decode error!'.format(s_msg))
            continue
        s_time = email.utils.mktime_tz(email.utils.parsedate_tz(s_msg.get('Date')))
        if int(1532744329) > s_time:
            print("Time overload!", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s_time)))
            print("Time is ", s_time)
            break
        res, charset = decode_header(s_msg.get('Subject'))[0]
        if charset:
            res = res.decode(charset)
            try:
                P_Num = re.search(r'[A-Z]{2}\d{10}', res).group(0)
            except Exception as msg:
                # print "标题为：", res
                continue
            
            if P_Num:
                # 获取工单号
                p_line['pro'] = P_Num
                # 获取申请组
                for P_group in dev_group:
                    if P_group.decode('utf-8') in res:
                        p_line['work'] = P_group
                        break
                # 获取申请内容
                P_data = res.split('><')
                if len(P_data) == 2:
                    p_line['data'] = P_data[-1]
                elif len(P_data) == 3:
                    p_line['data'] = P_data[-2]
                else:
                    sys.exit("标题错误！")
                # 获取操作类型
                for P_pro in subject_group:
                    # 获取其他信息
                    try:
                        # 操作类型,判断是间获取最早时间邮件
                        if P_pro.decode('utf-8') in res:
                            p_line['opreation'] = P_pro
                            p_line['time'] = s_time
                            p_line['puser'] = s_msg.get('From')
                    except Exception as msg:
                        print("Error is ", P_pro.decode('utf-8') )

                    try:
                        p_subj = res.split('【')[1].split('】')[0]
                    except Exception as msg:
                        print ("Subject Error")
                    
                    # 备机房
                    try:
                        if re.search(r'备机房', res).group(0):
                            p_line['slave_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s_time))
                            if p_line['operator'] != s_msg.get('From'):
                                p_line['operator'] = s_msg.get('From')
                            break
                    except Exception as msg:
                        print("不是备机房相关邮件")
                        # 主机房
                    try:
                        if re.search(r'主机房', res).group(0):
                            p_line['master_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s_time))
                            if p_line['operator'] != s_msg.get('From'):
                                p_line['operator'] = s_msg.get('From')
                            break
                    except Exception as msg:
                        print("不是主机房相关邮件")

                    # 验收
                    try:
                        if re.search(r'验收完成', res).group(0):
                            p_line['checktime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s_time))
                            if p_line['checkor'] != s_msg.get('From'):
                                p_line['checkor'] = s_msg.get('From')
                            break
                    except Exception as msg:
                        print("Error is 不是验收邮件")


                if not os.path.exists(list_path + p_line['pro']):
                    with open(list_path  + p_line['pro'], 'wb') as f:
                        pickle.dump(p_line, f)
                elif os.path.exists(list_path  + p_line['pro']):
                    with open(list_path  + p_line['pro'], 'rb') as f:
                        new_list = pickle.load(f)
                        if new_list["time"] == 0 or (new_list['time'] >= p_line['time']):
                            new_list['time'] = p_line['time']
                            new_list['puser'] = new_list['puser'] + "++" + p_line['puser']
                    for item in new_list:
                        try:
                            if not new_list[item]:
                                new_list[item] = p_line[item]
                            if new_list[item] == '':
                                new_list[item] = p_line[item]
                        except Exception as msg:
                            print "对比错误",msg

                    with open(list_path  + p_line['pro'], 'wb') as f:
                        pickle.dump(new_list, f)
                print "++++++++++END+++++++++"
s.logout()

for root, path, files in os.walk(list_path):
    for f_item in files:
        if f_item != 'List.txt':
            with open(list_path  +f_item, 'rb') as f:
                b = pickle.load(f)
                alist = ' '
                for item in b:
                    if alist.strip() == '':
                        alist = str(b[item])
                    elif alist.strip() != '':
                        alist = alist + ',' + str(b[item])
                alist = alist + '\n'
            with open(list_path + 'List.txt', 'a+') as f:
                f.write(alist)