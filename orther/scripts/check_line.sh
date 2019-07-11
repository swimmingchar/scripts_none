#!/bin/bash

swith_line(){
    # 获取本地IP，判断机房位置
    zabbixIP=`/sbin/ip addr | grep 'brd' | grep -v 'ff:ff'| grep -v '00:00' | awk '{print $2}' | awk -F'/' '{print $1}'| grep '10\.10\.10\.24'| wc -l`
    if [ "${zabbixIP}" == "1" ]; then
        echo 'NginxIP is in master!' > /tmp/temp.log
        URLIP='x.x.x.x:8888'
        engineRoom="master"
    else
        echo 'NginxIP is in Slave!' > /tmp/temp.log
        URLIP='x.x.x.x:8888'
        engineRoom="slave"
    fi
    
    # get lineswith
    swithed=`cat /var/tmp/scripts/line_swith`

    # 过滤多次相同切换
	if [ "${swithed}" != "$2" ];then
		if [ -n "$1" ] && [ "$2" != "detect" ];then
			/usr/bin/curl -s -l "http://${URLIP}/gateway-payservice-core/controller/netStatus/notify?engineRoom=${engineRoom}&payagte=$1&line=$2" > /var/tmp/scripts/swith_line.log
			
            # 过滤SUCCESS. 过滤成功，则标记过滤标识。
            swithed_s=`cat /var/tmp/scripts/swith_line.log | grep "SUCCESS"| wc -l`
            if [ "${swithed_s}" == "1" ];then
                echo $2 > /var/tmp/scripts/line_swith
            fi
            # 发送切换结果，不论获得的结果为成功或者失败。
            cat /var/tmp/scripts/swith_line.log | mutt -s "${engineRoom}机房线路切换至$2线路" shiwm@test.com
		fi
	fi

    # 探测API接口使用epcc线路
    if [ "$2" == "detect" ] && [ "$1" == "epcc" ];then
        /usr/bin/curl -s -m 5  "http://${URLIP}/gateway-payservice-core/controller/netStatus/notify?engineRoom=${engineRoom}&payagte=$1&line=$2" > /var/tmp/scripts/detect.log
        
        # 判断返回值是否为R 如过不是R 则发送邮件
        detect_condition=`cat /var/tmp/scripts/detect.log`
        if [ "${detect_condition}" != "R" ];then
            echo "API端口故障！" | mutt -s "网关API端口故障" shiwm@test.com
        fi
    fi
}

# check_line.sh [epcc/cup] [detect/slave/master]
swith_line $1 $2