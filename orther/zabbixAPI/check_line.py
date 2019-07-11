#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib
import pycurl
import sys, logging
from config import Config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    filename='/tmp/check_line.log',
                    filemode='ab+')


if __name__ = '__main__':
    conf = file('.\\line.conf')
    # for linux 
    # conf = file('../../system.conf')
