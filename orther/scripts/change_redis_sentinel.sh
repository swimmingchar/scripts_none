#!/bin/bash
# redis env
redis_sentinel_file='/home/redis/redis-cluster/redis-6379/etc/sentinel.conf'
redis_config_path='/home/redis/redis-cluster/redis-6379/etc/'
redis_cli='/home/redis/redis-cluster/redis-6379/bin/redis-cli'

alter_msg(){
    echo -e "\033[31m\033[01m $1 \033[0m"
}

notice_msg(){
    echo -e "\033[1m\033[32m $1 \033[0m"
}


# 备份setinel文件
cd ${redis_config_path}
/bin/cp {,Back_`date +%Y%m%d%H%S`}sentinel.conf

# 获取操作命令
redis_name=`${redis_cli} -p 26379 role| tail -1`
sentinel_remove_cli="sentinel remove ${redis_name}"
sentinel_monitor_cli="sentinel monitor ${redis_name} 10.10.5.200 6379 2"
sentinel_cmd1_cli=`grep "down-after-milliseconds" ${redis_sentinel_file}|grep -v ^#| awk '{print $1" set "$3" "$2" "$4}'`
sentinel_cmd2_cli=`grep "failover-timeout" ${redis_sentinel_file}| grep -v ^#| awk '{print $1" set "$3" "$2" "$4}'`
sentinel_cmd3_cli="sentinel set ${redis_name} parallel-syncs 1"
sentinel_cmd4_cli=`grep "auth-pass" ${redis_sentinel_file}| grep -v ^#| awk '{print $1" set "$3" "$2" "$4}'`
# sentinel_cmd5_cli="eval "grep failover-timeout ${redis_sentinel_file}| grep -v ^#| awk '{print $1" set "$3" "$2" "$4}'""

# 开始执行
alter_msg "exec sentinel remove:"
echo ${sentinel_remove_cli} | ${redis_cli} -p 26379
# cat ${redis_sentinel_file}
sleep 1

alter_msg "Set sentinel monitor:"
echo ${sentinel_monitor_cli} | ${redis_cli} -p 26379
notice_msg "`grep monitor ${redis_sentinel_file}`"
sleep 1

alter_msg "exec sentinel down-after-milliseconds："
# ${redis_cli} -p 26379 ${sentinel_cmd1_cli}
echo ${sentinel_cmd1_cli} | ${redis_cli} -p 26379
notice_msg "`grep "down-after-milliseconds" ${redis_sentinel_file}`"
sleep 1

alter_msg "exec sentinel failover-timeout："
echo ${sentinel_cmd2_cli} | ${redis_cli} -p 26379
# ${redis_cli} -p 26379 ${sentinel_cmd2_cli}
notice_msg "`grep "failover-timeout" ${redis_sentinel_file}`"
sleep 1

alter_msg "exec sentinel parallel-syncs："
echo  ${sentinel_cmd3_cli} | ${redis_cli} -p 26379

alter_msg "exec sentinel auth-pass："
echo ${sentinel_cmd4_cli} | ${redis_cli} -p 26379 
notice_msg "`grep "auth-pass" ${redis_sentinel_file}`"
echo -e "\033[1m\033[33m Redis sentinel Set Back OK！ \033[0m"