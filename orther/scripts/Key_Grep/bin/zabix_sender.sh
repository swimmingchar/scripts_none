#!/bin/bash
# zabix_sender.sh zabix_serv www.baidu.com 444 baidu-443 10.10.9.20

telnet_path=`which telnet`
zabbix_serv_ip=$1
addr=$2
port=$3
zab_key=$4
hostip=$5
zabbix_serv_port=10051
zabbix_sender_path='/usr/bin/zabbix_sender'


telnet_exec=`echo quit | timeout --signal=9 1 ${telnet_path} ${addr} ${port} 2>&1`
if [ -z "${telnet_exec}" ];then
    telnet_value=1
else
    telnet_value=0
fi
#zabbix sender
[ -f ${zabbix_sender_path} ] || zabbix_sender_path="./zabbix_sender"
# $ZBXSENDER -z $ZBXSERVER -p 10051 -s $HOSTNAME -k $IP-SmokLost -o ${tab[0]} -v | grep  "failed: 1" &> /dev/null
${zabbix_sender_path} -z ${zabbix_serv_ip} -p ${zabbix_serv_port} -s ${hostip} -k ${zab_key} -o ${telnet_value} -v | grep  "failed: 1" &> /dev/null