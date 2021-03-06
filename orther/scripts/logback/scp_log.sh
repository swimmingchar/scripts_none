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
y_day=`/bin/date -d  "5 days ago" +%Y-%m-%d`
#y_day="2019-05-22"
# 上次传输时间
l_day=$(cat ${local_path}.conf| head -1|awk -F'|' '{print $NF}')

# 删除日志时间
#d_day="2019-05-19"

# 本地压缩文件路径
zip_path=${local_path}.backup/${app}_${ip_name}_${y_day}.gz
# 上次传输文件路径
lzip_path=${local_path}.backup/${app}_${ip_name}_${l_day}.gz
# 本地删除文件路径
#dzip_path=${local_path}.backup/${app}_${ip_name}_${d_day}.gz


function rand() {
   min=$1
   max=$(($2-$min+1))
   num=$(date +%s%N)
   sleep $(($num%$max+$min))
}

# 判断是否获取备份中心IP
if [[ ${#backIP} == 0 ]]; then
    echo "获取备份中心IP地址失败："${ip}"。" >${local_path}.conf
    exit 1
fi

# ls -1 .|grep recon-core| grep -Po '.*2019.?06.?01.*'
args=".*$(echo ${y_day}|awk -F'-' '{print $1}').?$(echo ${y_day}|awk -F'-' '{print $2}').?$(echo ${y_day}|awk -F'-' '{print $3}').*"

# 临时文件夹
[[ -d ${local_path}.backup ]] || mkdir -p ${local_path}.backup
# 获取本地文件md5值
now_md5=$(/usr/bin/md5sum ${zip_path}|awk '{print $1}')
# 远端路径
remote_cmd="/backup/typeback/$(echo ${y_day}|awk -F'-' '{print $1}')/$(echo ${y_day}|awk -F'-' '{print $2}')/${app}/"
#l_remote_cmd="/backup/typeback/$(echo ${l_day}|awk -F'-' '{print $1}')/$(echo ${l_day}|awk -F'-' '{print $2}')/${app}/"


for i in $(seq 10)
do
    # 随机延时
    $(rand 10 180)
    # 上传文件
    /usr/bin/sshpass -p ${password_str} scp -rp ${zip_path} tomcat@${backIP}:${remote_cmd}
    if [[ $? == 0 ]]; then
        break
    fi
done

if [[ $? != 0 ]]; then
    echo "FAIL~连接备份中心失败.|"${y_day} > ${local_path}.conf
    exit 1
fi

yun_md5_str=$(/usr/bin/sshpass -p ${password_str} ssh tomcat@${backIP} "/usr/bin/md5sum ${remote_cmd}${app}_${ip_name}_${y_day}.gz")
yun_md5=$(echo ${yun_md5_str}| awk '{print $1}')
# 写入备份文件信息
ls -lh ${zip_path}| awk '{print $5,$NF}' >${local_path}.conf
# 对比MD5值并写入标识
if [[ "${now_md5}" == "${yun_md5}" ]]; then
    echo "${app}-${y_day}.tar.gz 复制完成！"
#    rm -f ${dzip_path}
else
    echo "${app}-${y_day}.tar.gz 复制失败！" > ${local_path}.fail_log
fi
# 完成备份
echo `date +%F" "%T`"日志备份动作完成。"
