#!/bin/bash
# eg:change_ip.sh BJ1-Ulpay-account-job-5-5 5.5
# set init env
echo "SET IP & Hostname"

# hostname file
host_file="/etc/hosts"
hosts_line1="127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4"
hosts_line2="::1         localhost localhost.localdomain localhost6 localhost6.localdomain6"
ip="10.10."$2
hostname=$1
hostname_file="/etc/sysconfig/network"

# add hosts
echo "add hosts & hostname"
sign=`echo $1| awk -F'-' '{print $1}'`
if [ ${sign} == "BJ1" ];then
    configcenter="x.x.x.x  www.configcenter.com"
    sign=master
elif [ ${sign} == "BJ2" ];then
    configcenter="x.x.x.x  www.configcenter.com"
    sign=slave
fi

echo "
${hosts_line1}
${hosts_line2}
${ip}  ${hostname}
${configcenter}
" > ${host_file}

# change hostname
`sed -i "s/^HOSTNAME=.*/HOSTNAME=$1/g" ${hostname_file}`
echo "Hostname is:"
`grep 'HOSTNAME' ${hostname_file}`

echo "change hosts file:"
`cat ${host_file}`

#get env
eth0_file="/etc/sysconfig/network-scripts/ifcfg-eth0"
eth1_file="/etc/sysconfig/network-scripts/ifcfg-eth1"

# change IPADDR
echo "change IP ADDR:"

if [ ${sign} == "master" ];then
    `sed -i "s/IPADDR=.*/IPADDR=${ip}/g" ${eth0_file}`





echo "Get Path env!...."
# network file
eth0_file="/etc/sysconfig/network-scripts/ifcfg-eth0"
eth1_file="/etc/sysconfig/network-scripts/ifcfg-eth1"
eth0_ip=`cat ${eth0_file}| grep -i "IPADDR"|awk -F'=' '{print $2}'`
eth0_gateway=`cat ${eth0_file}| grep -i "GATEWAY"|awk -F'=' '{print $2}'`

# route_file
route_file="/etc/sysconfig/static-routes"

# rotue="16.0/24 100.0/24 10.0/24"
# get route list
route_100="any net 10.10.100.0 netmask 255.255.255.0 dev eth1 "
route_16="any net 10.10.16.0 netmask 255.255.255.0 dev eth1 "
route_10="any net 10.10.10.0 netmask 255.255.255.0 dev eth1 "


# Tomcat_PATH
# tomcat_server_path="/home/tomcat/app/conf/server.xml"
# 增加业务IP 8080端口监听
#if [ -f ${tomcat_server_path} ]:then
#    /bin/sed -i 'N;72a\\t\taddress='\"${eth1_ip}\"'' ${tomcat_server_path}
#    echo "Tomcat address is: "`grep "address" ${tomcat_server_path}` >> ${ip_out}
#else
#    echo "ERROR: IN ${eth1_ip} server ${tomcat_server_path} is not exits!" >> ${ip_out}
#fi


# 检测是否有eth1文件
if [ ! -f "${eth1_file}" ];then
    cd /etc/sysconfig/network-scripts/
    cp -f ifcfg-eth0 ifcfg-eth1
    # Get ChangeIP
    eth0_ip_1=`grep 'IPADDR' ${eth0_file}| cut -d= -f 2| cut -d. -f 1`
    eth0_ip_2=`grep 'IPADDR' ${eth0_file}| cut -d= -f 2| cut -d. -f 2`
    eth0_ip_3=`grep 'IPADDR' ${eth0_file}| cut -d= -f 2| cut -d. -f 3`
    eth0_ip_4=`grep 'IPADDR' ${eth0_file}| cut -d= -f 2| cut -d. -f 4`
    eth1_ip_3=`echo ${eth0_ip_3}+200|/usr/bin/bc`
    eth1_ip=${eth0_ip_1}"."${eth0_ip_2}"."${eth1_ip_3}"."${eth0_ip_4}
    echo "Eth1-IP Time： "`/bin/date +%F" "%T` >> ${ip_out}
    echo "Eth1-IP: "${eth1_ip} >>  ${ip_out}
    /bin/sed -i "s/^IPADDR.*/IPADDR=${eth1_ip}/g" ${eth1_file}
    echo "Eth1-IP: "`grep 'IPADDR' ${eth1_file}` >> ${ip_out}

    # other config
    /bin/sed -i 's/DEFROUTE.*/DEFROUTE=no/g' ${eth1_file} 
    /bin/sed -i "s/eth0/eth1/g" ${eth1_file}
    # delete gateway,don't covered new route
    /bin/sed -i "/^GATEWAY.*/d" ${eth1_file}

else
    eth1_ip=`cat ${eth1_file}| grep -i "IPADDR"|awk -F'=' '{print $2}'`
    eth1_gateway=`cat ${eth1_file}| grep -i "GATEWAY"|awk -F'=' '{print $2}'`
    if [ ! -z $ {eth1_gateway} ];then
        /bin/sed -i "/^GATEWAY.*/d" ${eth1_file}
    fi
    # 写入时间
    echo "Eth1-IP： "`/bin/date +%F" "%T` >> ${ip_out}
    echo "Eth1-IP： "${eth1_ip} >> ${ip_out}
fi

# 清空静态路由文件
if [ ! -f "${route_file}" ];then
    echo ${route_100}$ >> ${route_file}
    echo ${route_16} >> ${route_file}
    echo ${route_10} >> ${route_file}
    echo "route_Time: "`/bin/date +%F" "%T` >> ${route_out}
    echo "statice Route is :" >> ${route_out}
    cat ${route_file} >> ${route_out}
fi

# 重启网路服务
/etc/init.d/network  restart

# 修改监听IP
sed -i "s/^#ListenAddress 0.0.0.0/ListenAddress ${eth1_ip}/g" /etc/ssh/sshd_config
/etc/init.d/sshd  restart
echo "-----END------" >> ${route_out}
echo "-----END------" >> ${ip_out}