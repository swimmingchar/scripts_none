#!/usr/bin/env bash
# 前提条件，脚本至备份中心需要做免密，需要安装sshpass工具，使用密码登陆备份主机
# 备份中心保存日志路径为:
# ~/logbackup/2019-06-12/194.231/${app_name}/log_back_file
# IP list
input_addr='172.18.194.231 172.18.194.232'
yycore_addr='172.18.194.233 172.18.194.234'
trade_addr='172.18.194.235 172.18.194.236'
out_addr='172.18.194.237 172.18.194.238'

# app in
#input_app='ally-gateway cust-gateway app-ally app-managent trade-gateway manage-portal boss-core'
input_app='ally-gateway cust-gateway trade-gateway manage-portal boss-core'
yycore_app='profit-core profit-task markting-core markting-task terminal-core account-core remit-core recon-core ally-core cust-core data-center-core'
trade_app='trade-core trade-transfer risk-core recommed-core'
out_app='tp-auth sms-core position-core sdchannel'

# 脚本下backfile文件夹内保存有当天压缩的文件
logs_path=/home/tomcat/logs/
# 登陆密码
pass_230='vByboYOcR1STKnU_jTzy'
# 获取当前主机IP
ip=`ifconfig eth0 |grep "inet addr"| cut -f 2 -d ":"|cut -f 1 -d " "`
# 获取IP后两位
ip_name=$(echo ${ip}|awk -F'.' {'print $3"."$4'})
# 备份中心IP
backIP='172.18.194.230'
# 备份时间
y_day=`/bin/date -d  "4 days ago" +%Y-%m-%d`


# 前置日志备份
for i in ${input_addr[@]} ; do
    if [[ "$i" == "$ip" ]]; then
        # 压缩应用
        for app in ${input_app[@]} ; do
            # ls -1 .|grep recon-core| grep -Po '.*2019.?06.?01.*'
            args=".*$(echo ${y_day}|awk -F'-' '{print $1}').?$(echo ${y_day}|awk -F'-' '{print $2}').?$(echo ${y_day}|awk -F'-' '{print $3}').*"
            cd ${logs_path} && ls -1 .|grep ${app}| grep -Po ${args}| xargs tar czvf ~/.backup/${app}-${y_day}.tar.gz --remove-files
            # 获取本地文件md5值
            now_md5=$(/usr/bin/md5sum ~/.backup/${app}-${y_day}.tar.gz|awk '{print $1}')
            remote_cmd="~/logbackup/${y_day}/${ip_name}/"
            # 创建文件夹
            /usr/local/bin/sshpass -p ${pass_230} ssh tomcat@${backIP} "mkdir -p ${remote_cmd}"
            # 上传文件位于
            /usr/local/bin/sshpass -p ${pass_230} scp ~/.backup/${app}-${y_day}.tar.gz tomcat@${backIP}:${remote_cmd}
            old_md5_str=$(/usr/local/bin/sshpass -p ${pass_230} ssh tomcat@${backIP} "/usr/bin/md5sum ${remote_cmd}${app}-${y_day}.tar.gz")
            old_md5=$(echo ${old_md5_str}| awk '{print $1}')
            if [[ "${now_md5}" == "${old_md5}" ]]; then
                echo "${app}-${y_day}.tar.gz 复制完成！"
            else
                echo "${app}-${y_day}.tar.gz 复制失败！" > .fail_log
            fi
        done
    fi
done


# 运营日志备份
for i in ${yycore_addr[@]} ; do
    if [[ "$i" == "$ip" ]]; then
        # 压缩应用
        for app in ${yycore_app[@]} ; do
            # ls -1 .|grep recon-core| grep -Po '.*2019.?06.?01.*'
            args=".*$(echo ${y_day}|awk -F'-' '{print $1}').?$(echo ${y_day}|awk -F'-' '{print $2}').?$(echo ${y_day}|awk -F'-' '{print $3}').*"
            cd ${logs_path} && ls -1 .|grep ${app}| grep -Po ${args}| xargs tar czvf ~/.backup/${app}-${y_day}.tar.gz --remove-files
            # 获取本地文件md5值
            now_md5=$(/usr/bin/md5sum ~/.backup/${app}-${y_day}.tar.gz|awk '{print $1}')
            remote_cmd="~/logbackup/${y_day}/${ip_name}/"
            # 创建文件夹
            /usr/local/bin/sshpass -p ${pass_230} ssh tomcat@${backIP} "mkdir -p ${remote_cmd}"
            # 上传文件位于
            /usr/local/bin/sshpass -p ${pass_230} scp ~/.backup/${app}-${y_day}.tar.gz tomcat@${backIP}:${remote_cmd}
            old_md5_str=$(/usr/local/bin/sshpass -p ${pass_230} ssh tomcat@${backIP} "/usr/bin/md5sum ${remote_cmd}${app}-${y_day}.tar.gz")
            old_md5=$(echo ${old_md5_str}| awk '{print $1}')
            if [[ "${now_md5}" == "${old_md5}" ]]; then
                echo "${app}-${y_day}.tar.gz 复制完成！"
            else
                echo "${app}-${y_day}.tar.gz 复制失败！" > .fail_log
            fi
        done
    fi
done

# 交易日志备份
for i in ${trade_addr[@]} ; do
    if [[ "$i" == "$ip" ]]; then
        # 压缩应用
        for app in ${trade_app[@]} ; do
            # ls -1 .|grep recon-core| grep -Po '.*2019.?06.?01.*'
            args=".*$(echo ${y_day}|awk -F'-' '{print $1}').?$(echo ${y_day}|awk -F'-' '{print $2}').?$(echo ${y_day}|awk -F'-' '{print $3}').*"
            cd ${logs_path} && ls -1 .|grep ${app}| grep -Po ${args}| xargs tar czvf ~/.backup/${app}-${y_day}.tar.gz --remove-files
            # 获取本地文件md5值
            now_md5=$(/usr/bin/md5sum ~/.backup/${app}-${y_day}.tar.gz|awk '{print $1}')
            remote_cmd="~/logbackup/${y_day}/${ip_name}/"
            # 创建文件夹
            /usr/local/bin/sshpass -p ${pass_230} ssh tomcat@${backIP} "mkdir -p ${remote_cmd}"
            # 上传文件位于
            /usr/local/bin/sshpass -p ${pass_230} scp ~/.backup/${app}-${y_day}.tar.gz tomcat@${backIP}:${remote_cmd}
            old_md5_str=$(/usr/local/bin/sshpass -p ${pass_230} ssh tomcat@${backIP} "/usr/bin/md5sum ${remote_cmd}${app}-${y_day}.tar.gz")
            old_md5=$(echo ${old_md5_str}| awk '{print $1}')
            if [[ "${now_md5}" == "${old_md5}" ]]; then
                echo "${app}-${y_day}.tar.gz 复制完成！"
            else
                echo "${app}-${y_day}.tar.gz 复制失败！" > .fail_log
            fi
        done
    fi
done



# 接出日志备份
for i in ${out_addr[@]} ; do
    if [[ "$i" == "$ip" ]]; then
        # 压缩应用
        for app in ${out_app[@]} ; do
            # ls -1 .|grep recon-core| grep -Po '.*2019.?06.?01.*'
            args=".*$(echo ${y_day}|awk -F'-' '{print $1}').?$(echo ${y_day}|awk -F'-' '{print $2}').?$(echo ${y_day}|awk -F'-' '{print $3}').*"
            cd ${logs_path} && ls -1 .|grep ${app}| grep -Po ${args}| xargs tar czvf ~/.backup/${app}-${y_day}.tar.gz --remove-files
            # 获取本地文件md5值
            now_md5=$(/usr/bin/md5sum ~/.backup/${app}-${y_day}.tar.gz|awk '{print $1}')
            remote_cmd="~/logbackup/${y_day}/${ip_name}/"
            # 创建文件夹
            /usr/local/bin/sshpass -p ${pass_230} ssh -n tomcat@${backIP} "mkdir -p ${remote_cmd}"
            # 上传文件位于
            /usr/local/bin/sshpass -p ${pass_230} scp ~/.backup/${app}-${y_day}.tar.gz tomcat@${backIP}:${remote_cmd}
            old_md5_str=$(/usr/local/bin/sshpass -p ${pass_230} ssh -n tomcat@${backIP} "/usr/bin/md5sum ${remote_cmd}${app}-${y_day}.tar.gz")
            old_md5=$(echo ${old_md5_str}| awk '{print $1}')
            if [[ "${now_md5}" == "${old_md5}" ]]; then
                echo "${app}-${y_day}.tar.gz 复制完成！"
            else
                echo "${app}-${y_day}.tar.gz 复制失败！" > .fail_log
            fi
        done
    fi
done