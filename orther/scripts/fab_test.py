#!/usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import env, hosts, run, local,execute, cd
from fabric.colors import *

# env.hosts=["172.10.1.31",]
# env.user = 'root'
# env.password = "123456"
# self.passwd="123456"
# self.keyfile="C:\\Users\\s\\.ssh\\id_rsa.pub"

def get_uname():
    with cd('c:'):
        a = local("dir")
    print a


if __name__=="__main__":
    execute(get_uname)