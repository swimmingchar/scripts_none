#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.

class Host(models.Model):
    hostname = models.CharField(u"主机名", max_length=50, unique=True)
    ip = models.GenericIPAddressField(u"IP地址", null=False)
    os = models.CharField(u"系统版本", max_length=30, blank=True)
    cpu_p = models.CharField(u"物理核心数", max_length=10, blank=True)

class hist_ip(models.Model):
    iplist = models.CharField(u"IP列表", max_length=50, null=True)