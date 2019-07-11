#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, datetime, time, re, os
from datetime import datetime
from datetime import timedelta
from email.header import decode_header
import pickle, click
from imapclient import IMAPClient

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# MymailList 添加邮件列表
mymail_list = dict()
# work_list已收集工单列表
work_list = list()

@click.command()
@click.option('--day',default=7,help="邮件天数")
@click.option('--mail_user',prompt="邮箱名",help="邮箱用户名前缀")
@click.option('--mail_passwd',prompt="密码",help="邮箱密码",hide_input=True)
def getmailObj(day,mail_user,mail_passwd):
    global end_day
    end_day = int(day)*86400
    global imapObj
    imapObj = IMAPClient('imap.mxhichina.com',ssl=True).login(mail_user,mail_passwd)

def subject_decode(subject):
    res, charset = decode_header(subject)[0]
    return res.decode(charset)

<<<<<<< HEAD
def split_subject(subject,char):
    global sub_num
    try:
        for item in subject.split(char):
            if ">" in item:
                split_subject(item,">")
                sub_num = sub_num + 1
            if len(item.strip()) != 0 and item.strip() != work_list["Numb"]:
                work_list["title" + str(sub_num)] = item
                sub_num = sub_num + 1
    except:
        pass


# @click.command()
# @click.option('--day',default=7,help="邮件天数")
# @click.option('--user',prompt="邮箱名:",help="邮箱用户名前缀")
# @click.option('--passwd',prompt="密码:",help="邮箱密码")
if __name__=="__main__":
    # 时间处理
    start_time = int(time.time())
    end_time = start_time - 7 * 86400
    # end_time = start_time - day * 86400
=======
if __name__ == '__main__':
    imapObj = getmailObj()
    # 时间处理
    start_time = int(time.time())
    end_time = start_time - 1
>>>>>>> a0615bc6a38f3891202a5720072c9bb300500e11
    search_time = datetime.fromtimestamp(end_time)
    print search_time
    # 清空pro_list文件夹内文件
    os.system("rm -f ./pro_list/*")

    # imapObj = imapclient.IMAPClient('imap.mxhichina.com', ssl=True)
    # imapObj.login("shiwm@xxxxxx.com","xxxxxxxx")
    # imapObj.login(user,passwd)
    # print("The mail date is: %s" % get_data())

    for path,root,folder in imapObj.list_folders():
        if folder != '监控报警':
            print("\n\n默认文件夹名称：%s; 根路径为: %s; 邮件夹名称: %s\n" %(path, root, folder.decode('utf-8')))
            imapObj.select_folder(folder, readonly=True)
            UIDs = imapObj.search([u'SINCE', search_time])
            print("%s 目录，共有 %i 封邮件。\n" %(folder, len(UIDs)))

            for msgid, data in imapObj.fetch(UIDs, ['ENVELOPE']).items():
                # 获取邮件信息
                envelope = data[b'ENVELOPE']
                # 获取发件人
                from_mail = envelope.sender[0].name
                # 邮件接收时间
                from_time = int(time.mktime(envelope.date.timetuple()))
                # 解码标题
                try:
                    subject = subject_decode(envelope.subject.decode())
                except TypeError:
                    print("%s 解码错误, 邮件时间：%s, 邮件标题：%s\n" %(msgid,time.strftime("%Y-%m-%d %H:%M:%S",from_time),envelope.subject) )
                    subject = envelope.subject.decode()
                
                # 工单列表
                gd_number = dict()
                # 解析标题
                try:
                    # work_list["Numb"] = re.search(r'[a-zA-z]{2}[0-9]{10}',subject).group(0)
                    gd_number['number'] = str(re.search(r'[a-zA-Z]{2}[0-9]{10}',subject).group(0))
                    print gd_number
                    # 判断是否分析
                    if gd_number['number'] in work_list:
                        with open('./pro_list/' + gd_number['number'],'rb') as f:
                            # 加载工单信息
                            gd_number = pickle.load(f)
                            # 更新开始时间
                            if from_time < int(gd_number['start_time']) :
                                gd_number['start_per'] = from_mail
                                gd_number['start_time'] = from_time
                                gd_number['start_title'] = subject
                            #更新截止时间
                            if from_time > int(gd_number['end_time']) :
                                gd_number['end_time']  = from_time
                                gd_number['end_per'] = from_mail
                                gd_number['end_title'] = subject
                    else:
                        gd_number['start_per'] = gd_number['end_per'] = from_mail
                        gd_number['start_time'] = gd_number['end_time'] = from_time
                        gd_number['start_title'] = gd_number['end_title'] = subject
                    
                    with open('./pro_list/' + str(gd_number['number']),'wb') as f:
                        pickle.dump(gd_number,f)
                except Exception as msg:
                    print("Error is %s" % msg)
                    sys.exit()

        for root, path, files in os.walk('./pro_list/'):
            for f_item in files:
                if f_item != 'List.txt':
                    with open('./pro_list/' + f_item, 'rb') as f:
                        b = pickle.load(f)
                        alist = ""
                        for item in b:
                            alist = alist + '^' + item
                        alist = f_item + alist + '\n'
                    with open('./pro_list/List.txt', 'a+') as f:
                        f.write(alist)


                



