#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging, sys, os

from kazoo.client import KazooClient


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

zkhosts = 'IP1:2181,ip2:2181,ip3:2181,ip4:2181,ip5:2181'

zk = KazooClient(hosts=zkhosts)
try:
    zk.start
except Exception as emsg:
    logging.info("ZK Start eror:%s" % emsg)

