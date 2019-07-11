#!/bin/bash

# 定时删除7天之前文件
# 使用方法 del_unzip_file.sh find /backup/allunzip[需要删除文件的路径]  7[删除文件的时间，单位天]
# 手动开启
# [ $# -ne 2 ] && exit
# echo -e "USE eg:\n\033[1;41;33mdel_unzip_file.sh find /backup/allunzip[需要删除文件的路径]  7[删除文件的时间，单位天]\033[0m\n\033[1;41;33m你输入的命令为：$0 $1 $2\033[0m\n\033[1;41;33m如果正确，请输入yes\033[0m"
# read command
# [ ${command} -ne "yes" ] && exit
unzip_path=$1
# 删除时间。单位：天
del_day=$2
# del_file_name
del_file_name=/tmp/del_file_`date -d "1 days ago" +%Y%m%d'-'%H%M%S`.list

find ${unzip_path} -type f -mtime +${del_day} > ${del_file_name}
while read line;
do
    if [ -f ${line} ];then
        echo "rm -f ${line}" >>/tmp/del_log_`date -d "1 days ago" +%Y%m%d`.log
        rm -f ${line}
        [ $? -ne 0 ] && echo 'DELETE ${line} 失败' >> /tmp/del_file_error.log
    else
        echo ${line}" 删除失败，文件不存在!" >> /tmp/del_file_error.log
    fi
done < ${del_file_name}