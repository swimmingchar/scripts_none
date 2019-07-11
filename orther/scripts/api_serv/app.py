#!/usr/bin/env python
# -*- coding:utf-8 -*-

# api url : http://127.0.0.1:67690/getuserinfo/api/v1.0/info/[username]

from flask import Flask
import spwd

app = Flask(__name__)

@app.route('/getuserinfo/api/v1.0/info/<str:user_name>', method=['GET'])
def get_info(user_name):
    return spwd.getspname(user_name).sp_max