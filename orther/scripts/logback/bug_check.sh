#!/usr/bin/env bash

# 脚本下backfile文件夹内保存有当天压缩的文件
logs_path=/home/tomcat/logs/
# 登陆密码
password_str=''
# 获取当前主机IP
ip=`/sbin/ifconfig eth0 |grep "inet addr"| cut -f 2 -d ":"|cut -f 1 -d " "`
# 获取IP后两位
ip_name=$(echo ${ip}|awk -F'.' {'print $3"."$4'})
# 应用名
app_t1=$(echo `hostname`|cut -d '-' -f2-)
# 删除IP
app_t2=$(echo ${app_t1%'-'*})
# 获取小写应用名
app=$(echo ${app_t2,,})
# 判断机房位置
host_temp=$(hostname|cut -c 1-3)
host_signe=$(echo ${host_temp,,})

# 备份中心IP
if [[ "${host_signe}" == "bj1" ]]; then
    backIP='10.10.10.241'
elif [[ "${host_signe}" == "bj2" ]]; then
    backIP='10.10.30.241'
fi
# 程序运行路径
local_path=/home/tomcat/

function rand() {
   min=$1
   max=$(($2-$min+1))
   num=$(date +%s%N)
   sleep $(($num%$max+$min))
}


for i in $(seq 6)
do
    remote_cmd=/backup/typeback/2019/0${i}/${app}/
    file=$(ls -1 /home/tomcat/.backup/| grep 2019-0$i)
    echo "start transfer $i mouth!"
    if [[ ${file} != "" ]]; then
        $(rand 1 90)
        # 创建当前远端文件夹
        /usr/bin/sshpass -p ${password_str} ssh -o stricthostkeychecking=no tomcat@10.10.10.241 "[[ -d ${remote_cmd} ]] || mkdir -p ${remote_cmd}"
        # 文件传输
        cd  /home/tomcat/.backup/ && /usr/bin/sshpass -p ${password_str} /usr/bin/scp -rp ${file} tomcat@10.10.10.241:${remote_cmd}
    fi

done

if [[ $? != 0 ]];then
    echo "FAIL~连接备份中心失败.|"${ip} > ${local_path}.conf
    exit 1
fi