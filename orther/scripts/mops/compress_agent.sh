#!/usr/bin/env bash

# compress_agent.sh appname thisappip datatime[20190516] backserver_password
export LANG="en_US.UTF-8"

app_path=$1
app_ip=$2
com_data=$3
backserver_passwd=$4

log_path='/home/tomcat/logs'
local_zippath='/home/tomcat/magent/magent/zipfile'



#!/bin/sh
CHECK_TIME=2        #检测2次
check(){
    curl -m2 127.0.01:3128 > /dev/null 2>&1
    return $?
}

while [ $CHECK_TIME -ne 0 ]
do
    let "CHECK_TIME-=1"
    check
    SQUID_OK=$?

    if [ $SQUID_OK -eq 0 ]; then
        exit 0
    fi

    if [ $SQUID_OK -ne 1 ] && [ $CHECK_TIME -eq 0 ]; then
        exit 1
    fi
done





