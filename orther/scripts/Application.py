#!/usr/bin/python
"""
统计应用每秒钟访问次数
脚本参数：
    0：统计前一天应用每秒访问次数
    1：生成前一天应用最大访问次数和所在时间报告
"""
import sys
import datetime
import pymongo
import oracle
import mail

class AppStatistics(object):
    """
    统计应用程序各类统计信息
    """
    def __init__(self):
        self.client = pymongo.MongoClient('10.10.2.145', 20000)
        self.targetdb = self.client.get_database('log')
        self.dburl = 'yangwei/yangwei@10.10.10.40/DBMGR'

    def insert_data(self, datalist):
        """
        将统计结果保持到Oracle数据库
        """
        sql = ('INSERT INTO yangwei.t_rpt_app_acc_freq(app_name, acc_time, num_req) '
               'VALUES(:1, :2, :3)')
        mgrdb = oracle.Database(self.dburl)
        mgrdb.insert_many(sql, datalist)
        mgrdb.db_close()

    def get_app_freq(self, starttime, endtime):
        """
        统计指定时间段内的应用请求频率
        param：
            starttime，endtime：字符串格式时间，格式：%Y%m%d%H%M%S
        """
        # 分表表名
        col_name = 'simpleLog' + starttime[:6]
        # print(col_name)
        col = self.targetdb.get_collection(col_name)
        # print(pipeline)
        # 统计开始时间
        btime = starttime
        maindata = []
        while btime < endtime:
            # 获取统计时间间隔的下限时间
            etime = (datetime.datetime.strptime(btime, '%Y%m%d%H%M%S')
                + datetime.timedelta(seconds=1)).strftime('%Y%m%d%H%M%S')
            # mongodb统计条件

            pipeline = [
                {"$match": {"startTime": {"$gte": btime, "$lt": etime}}},
                {"$group": {"_id":"$appName", "total":{"$sum":1}}}
            ]
            result = list(col.aggregate(pipeline))
            for value in result:
                maindata.append([value.get("_id"), btime, value.get("total")])
            btime = etime
            # print(btime,etime)
        return maindata

    def save_data(self, starttime=None, stoptime=None, step=None):
        """
        保持数据
        """
        # 如果传入的dayt为空，则统计前一天的数据
        if starttime is None:
            starttime = (datetime.date.today()
                + datetime.timedelta(days=-1)).strftime('%Y%m%d') + '000000'
        if stoptime is None:
            stoptime = datetime.date.today().strftime('%Y%m%d') + '000000'

        # 每次数量数据的时间间隔，默认每次查询1小时的数据
        if step is None:
            step = 1
        # print(starttime, stoptime, step
        while starttime < stoptime:
            endtime = (datetime.datetime.strptime(starttime, '%Y%m%d%H%M%S')
                + datetime.timedelta(minutes=step)).strftime('%Y%m%d%H%M%S')
            data = self.get_app_freq(starttime, endtime)
            # print(starttime, data)
            self.insert_data(data)
            starttime = endtime

    def generate_report_daily(self):
        """
        每天按照应用统计前一天应用最大访问频率，每秒访问次数，生成html格式邮件正文以及邮件标题
        """
        daytime = (datetime.date.today() + datetime.timedelta(days=-1))
        btime = daytime.strftime('%Y%m%d') + '000000'
        etime = daytime.strftime('%Y%m%d') + '235959'
        sql = (
            "SELECT app_name,to_date(acc_time,'yyyymmddhh24miss') time_req,num_req FROM ( "
            "SELECT app_name,acc_time,num_req, "
            "row_number() OVER(PARTITION BY app_name,SUBSTR(acc_time,1,8) ORDER BY num_req DESC) rn "
            "FROM yangwei.t_rpt_app_acc_freq "
            "WHERE acc_time BETWEEN :btime AND :etime "
            "AND app_name IN ('merc-gateway-web','merc-payoutgateway-web')) "
            "WHERE rn = 1")
        mgrdb = oracle.Database(self.dburl)
        # print(sql, btime, etime)
        result = mgrdb.get_cursor_result(sql, 0, btime=btime, etime=etime)
        # mgrdb.insert_many(sql, datalist)
        mgrdb.db_close()
        # print(result)
        subject = '应用访问频率统计<' + daytime.strftime('%Y-%m-%d') + '>'
        if result:
            tabtext = """<h2></h2>
            <table>
            <tr>
              <th>应用名称</th>
              <th>请求时间</th>
              <th>最大访问次数</th>
            </tr>"""
            for value in result:
                tabtext += """
                <tr>
                  <td>""" + value[0] + """</td>
                  <td>""" + str(value[1]) + """</td>
                  <td>""" + str(value[2]) + """</td>
                </tr>"""
            tabtext += """
            </table>"""
        # 邮件html格式正文
        html = (
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')

        html += """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <style type='text/css'>
        table
          {
          font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
          width:50%;
          border-collapse:collapse;
          align:center;
          }

        td, th
          {
          font-size:1em;
          text-align:center;
          border:1px solid LightSlateGray;
          padding:3px 7px 2px 7px;
          }

        th
          {
          font-size:1.1em;
          padding-top:5px;
          padding-bottom:4px;
          background-color:MediumBlue;
          color:White;
          }

        td
	     {
	     text-align:left;
	     }

        </style>
        </head>

        <body>
        """ + tabtext + """
        </body>
        </html>"""
        return subject, html


if __name__ == "__main__":
    # 获取开始时间
    # daytime = datetime.datetime.today() + datetime.timedelta(days=-1)
    # 统计开始时间
    # btime = daytime.strftime('%Y%m%d') + '000000'
    # 统计结束时间
    APP = AppStatistics()
    # DATA = APP.get_app_freq('20180801120000', '20180801120001')
    print(sys.argv)
    if sys.argv[1] == '0':
        APP.save_data()
        # APP.save_data('20180801000000', '2018090000000')
    elif sys.argv[1] == '1':
        DATA = APP.generate_report_daily()
        # for i in DATA:
        # print(i)
        MAIL = mail.EmailManager("oracle@mail.ul.com", '', 'mail.ul.com')
        TOADDR = ['dba@test.com']
        # TOADDR = ['shiwm@test.com']
        MAIL.send_mail(TOADDR, DATA[0], DATA[1])
    else:
        raise 'Error args, Please input argv [0, 1]'
