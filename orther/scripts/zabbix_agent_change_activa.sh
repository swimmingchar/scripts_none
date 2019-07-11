#!/bin/bash
# @Author: OBKoro1
# @Date: 2018-09-14 13:38:50
# @LastEditors: OBKoro1
# @LastEditTime: 2018-09-14 13:39:12
# @Description: 将zabbix的被动模式改为主动模式,基于原有启用状态时改变

#-------------更改---------------
# 1、注释第95行，气内容为：Server=x.x.x.x
# 2、更改第147行数据呗本地IP，其内容为：Hostname=x.x.x.x
# 
#——------------添加---------------
# 1、第121行添加StartAgents=0；
# 2、第179添加HostMetadataItem=system.uname;
# 3、第188行添加RefreshActiveChecks=120;
# 4、第206行添加BufferSize=300;
# 5、第241行添加Timeout=5;

err_msg(){
    echo -e "\033[31m\033[01m $1! \033[0m"
}

apperd_msg(){
    echo -e "\033[1m\033[32m $1. \033[0m"
}

main(){
    # default var
    local date_sign=`date +%Y%m%d%H%M%S`
    local zabbix_path="/etc/zabbix/zabbix_agentd.conf"
    local comd_user=`whoami`
    local ip_addr=`/sbin/ifconfig|sed -n '/eth0/{N;/inet/p}'| sed -n '/inet addr/s/^[^:]*:\([0-9.]\{7,15\}\) .*/\1/p'`

    # env test, if not use root,exit
    if [ "${comd_user}" != "root" ];then
        echo "user is not root!"
        exit
    fi

    # back conf
    /bin/cp ${zabbix_path}{,_bak${date_sign}}

    #更改配置文件
    local line_serv=`grep ^Server= ${zabbix_path}| wc -l`
    if [ "${line_serv}" == "1" ];then
        sed -i 's/^Server=/# Server=/g' ${zabbix_path}
        apperd_msg "SvererIP changed!"
    else
        err_msg "Server option is ${line_serv}"
    fi

    local line_hostname=`grep ^Hostname= ${zabbix_path}| wc -l`
    if [ "${line_hostname}" == "1" ];then
        sed -i "s/^Hostname=.*/Hostname=${ip_addr}/g" ${zabbix_path} 
        apperd_msg "Hostname changed!"
    else
        err_msg "Hostname option is ${line_hostname}"
    fi

    # 增加配置
    # StartAgents
    local line_startagent=`grep ^StartAgents= ${zabbix_path}| wc -l`
    if [ "${line_startagent}" == "0" ];then
        sed -i '120a\StartAgents=0' ${zabbix_path}
        apperd_msg "StartAgents Add!"
    else
        err_msg "StartAgents Option is ${line_startagent}"
    fi

    # HostMetadataItem
    local line_metadata=`grep ^HostMetadataItem= ${zabbix_path} | wc -l`
    if [ "${line_metadata}" == "0" ];then
        sed -i '178a\HostMetadataItem=system.uname' ${zabbix_path}
        apperd_msg "HostMetadata is Add!"
    else
        err_msg "HostMetadata Option is ${line_metadata}"
    fi

    # RefreshActiveChecks=120;
    local line_refresh=`grep ^RefreshActiveChecks= ${zabbix_path} | wc -l`
    if [ "${line_refresh}" == "0" ];then
        sed -i '187a\RefreshActiveChecks=120' ${zabbix_path}
        apperd_msg "RefreshActiveChecks is Add!"
    else
        err_msg "RefreshActiveChecks Option is ${line_refresh}"
    fi

    # BufferSize=300;
    local line_buffer=`grep ^BufferSize= ${zabbix_path} | wc -l`
    if [ "${line_buffer}" == "0" ];then
        sed -i '204a\BufferSize=300' ${zabbix_path}
        apperd_msg "BufferSize is Add!"
    else
        err_msg "BufferSize Option is ${line_buffer}"
    fi

    # Timeout=5;
    local line_timeout=`grep ^Timeout= ${zabbix_path} | wc -l`
    if [ "${line_timeout}" == "0" ];then
        sed -i '240a\Timeout=5' ${zabbix_path}
        apperd_msg "Timeout is Add!"
    else
        err_msg "Timeout Option is ${line_timeout}"
    fi

    # UnsafeUserParameters=1
    local line_Parameters=`grep ^UnsafeUserParameters= ${zabbix_path} | wc -l`
    if [ "${line_Parameters}" == "0" ];then
        sed -i '289a\UnsafeUserParameters=1' ${zabbix_path}
        apperd_msg "UnsafeUserParameters is Add!"
    else
        err_msg "UnsafeUserParameters Option is ${line_Parameters}"
    fi

}

main