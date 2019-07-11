#!/usr/bin/env python
# -*- coding:utf-8 -*-

import click
@click.command()
@click.option("--date",dafualt=7, help="输入天数.")
@click.option("--user", prompt="邮箱用户名前缀:", help="获取邮箱用户名.")
@click.option("--password", prompt="输入密码:", help="获取邮箱密码.")


if __name__ == '__main__':
    
