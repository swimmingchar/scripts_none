#!/usr/bin/env bash
# 更改环境变量，保证发送内容可以放在邮件正文中
#export LANG=en_US.UTF-8
LANG="en_US.UTF8" ; export LANG
# 收集所有资料汇总发送邮件
# /bin/mail -s "主题"  收件地址< 文件(邮件正文.txt)
# /bin/mail -s "邮件主题"  1968089885@foxmail.com < /data/findyou.txt

host_file=/home/tomcat/shiwm-service/io_scripts/logback-host

ansible_bin=/usr/bin/ansible

temp_file=/tmp/tmp_ansible.log

sent_to="shiweiming@elinkdata.cn"

# 时间，需要和logback内的y-day保持一致
y_day=`/bin/date -d  "5 days ago" +%Y`

res_file=/tmp/res.txt

subject="主机房`/bin/date +%Y-%m-%d`日志备份摘要"

# 获取执行结果
${ansible_bin} -i ${host_file} all -m raw -a 'cat ~/.conf' > ${temp_file}

# 格式化返回结果
# 删除头行,包含">>"
/bin/sed -i '/>>/d' ${temp_file}
# 删除信息行，开头包含"Shared"
/bin/sed -i '/^Shared/d' ${temp_file}
# 删除空行，"^$"
/bin/sed -i '/^$/d' ${temp_file}
# 添加文本信息
echo "采集信息 "`wc -l ${temp_file}| awk '{print $1}'`" 行。" > ${res_file}


#获取成功备份节点数量
suecc_num=$(grep ^[0-9] ${temp_file}| wc -l)
# 写入节点数
echo "日志备份节点 ${suecc_num} 个。" >> ${res_file}
suecc_size=$(grep ^[0-9] ${temp_file}|awk '{sum += $1}; END {print sum}')
# 写入备份日志总量
echo "日志备份大小为 $( echo "scale=2;${suecc_size}/(1024*1024)"|/usr/bin/bc) MB。" >> ${res_file}
fail_num=$(grep -v ^[0-9] ${temp_file}|wc -l )
# 写入错误行数
echo "备份异常节点数 ${fail_num} 个。" >> ${res_file}
# 写入错误内容
echo -e "\n"  >> ${res_file}
echo "异常内容如下：" >> ${res_file}
/bin/grep -v ^[0-9] ${temp_file} >> ${res_file}
echo -e "\n" >> ${res_file}
# 写入结尾
echo "数据统计于："`/bin/date +%Y-%m-%d`"。" >> ${res_file}

# 发送邮件
cat ${res_file} | /bin/mail -s "${subject}" ${sent_to}