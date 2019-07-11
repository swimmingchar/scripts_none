#!/usr/bin/env bash
# 前提条件，需要安装sshpass工具，使用密码登陆备份主机
# 备份中心保存日志路径为:
# /backup/typeback/2019/05/${app_name}/${app_name}_${ip}_${date}.zip

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

# 备份时间
#y_day=`/bin/date -d  "4 days ago" +%Y-%m-%d`
y_day="2019-05-22"
# 上次传输时间
l_day=$(cat ${local_path}.conf| head -1|awk -F'|' '{print $NF}')

# 删除日志时间
d_day="2019-05-19"

# 本地压缩文件路径
zip_path=${local_path}.backup/${app}_${ip_name}_${y_day}.gz
# 本地删除文件路径
dzip_path=${local_path}.backup/${app}_${ip_name}_${d_day}.gz

# 判断是否获取备份中心IP
if [[ ${#backIP} == 0 ]]; then
    echo "获取备份中心IP地址失败："${ip}"。" >${local_path}.conf
    exit 1
fi

# rsync 变量
rsyn_bin=/usr/bin/rsync



function rand() {
   min=$1
   max=$(($2-$min+1))
   num=$(date +%s%N)
   sleep $(($num%$max+$min))
}



function tran_success() {

}

function main(){
    local zip_state=""
    # ls -1 .|grep recon-core| grep -Po '.*2019.?06.?01.*'
    args=".*$(echo ${y_day}|awk -F'-' '{print $1}').?$(echo ${y_day}|awk -F'-' '{print $2}').?$(echo ${y_day}|awk -F'-' '{print $3}').*"
    # 判断是否有创建本地备份临时文件夹，以及相关其他文件夹
    # 临时文件夹
    [[ -d ${local_path}.backup ]] || mkdir -p ${local_path}.backup
    # 判断以及过滤文件
    file=`cd ${logs_path} && ls -1 .| grep -Po ${args}`
    num_b=`cd ${logs_path} && ls -1 .| grep -Po ${args}| wc -l`
    # 开始压缩文件
    if [[ ${num_b} != 0 ]];then
        cd ${logs_path} && tar czvf ${zip_path} ${file} --remove-files
        zip_state="1"
    fi
    # 获取本地文件md5值放在.md5文件内
    echo $(/usr/bin/md5sum ${zip_path}) > ${zip_path}.md5



    for i in $(seq 5)
    do
        # 等待随机时间后传输
        $(rand 60 300)
        # rsync -avzcWR --port=8873 agentserver-portal_3.19_2019-06*.gz user@10.10.10.241::main-backup/2019/06/agentserver-portal
        # 文件传输


        if [[ $? == 0 ]]; then
            tran_success
            exit 0
        fi
    done
}







$(main|tee >/tmp/temp.logs)

