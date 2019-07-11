from django.shortcuts import render, HttpResponse
from django.http import HttpRequest
import requests
from cmdb.models import Host
import json
# Create your views here.


def hello(request):
    return HttpResponse("akajshfkdshfk")

def collect(request):
    date_json = json.loads(request.body)
    if request.method == 'POST':
        hostname = date_json['hostname']['hostname']
        ip = date_json['hostname']['ipaddr']
        os = date_json['hostname']['os']
        cpu_p = date_json['cpu']['physical']
        #pylint问题，可以忽略
        try:
            host = Host.objects.get(hostname=hostname)
        except Exception as msg:
            print('collect save is error:', msg)
            host = Host()
        host.hostname = hostname
        host.ip = ip 
        host.os = os
        host.cpu_p = cpu_p
        host.save()
        return HttpResponse('Post save successful!')
    else:
        return HttpResponse('No data save!')