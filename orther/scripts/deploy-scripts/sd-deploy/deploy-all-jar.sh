#!/usr/bin/env bash
# IP list
input_addr='172.18.194.231 172.18.194.232'
yycore_addr='172.18.194.233 172.18.194.234'
trade_addr='172.18.194.235 172.18.194.236'
out_addr='172.18.194.237 172.18.194.238'

# app in
input_app='ally-gateway cust-gateway app-ally app-managent trade-gateway manage-portal boss-core'
yycore_app='profit-core profit-task markting-core markting-task terminal-core account-core remit-core recon-core ally-core cust-core data-center-core'
trade_app='trade-core trade-transfer risk-core recommed-core'
out_app='tp-auth sms-core position-core sdchannel'

# 历史文件根目录下创建.bak文件，内部放

err_msg(){
    echo -e "\033[31m\033[01m$* \n \033[0m"
}

ok_msg(){
    echo -e "\033[1m\033[32m$* \n \033[0m"
}

alarm_msg(){
    echo -e "\033[1m\033[33m$* \n \033[0m"
}

# 记录上线版本
sign_version(){
    local app_all_name=$1
    local app_ip=$2
    local app_name=$(echo ${app_all_name}|awk -F'_' '{print $1}')
    version_path=/home/manager/.ver
    [[ -d ${version_path} ]] || mkdir -p ${version_path}
    # 不论是否有文件
    if [[ -f ${version_path}/${app_name} ]];then
        echo ${app_all_name} >> ${version_path}/${app_name}
    fi
    # 删除脚本
    numb_ver=$(cat ${version_path}/${app_name}| wc -l)
    if [[ ${numb_ver} -gt 2 ]];then
        local app_all_name=$(echo ${version_path}/${app_name} | head -1)
        # 删除就版本
        ssh tomcat@${app_ip} "cd ~/release && rm -rf ${app_all_name}*"
        # 删除第一行
        sed -i '1 d' ${version_path}/${app_name}
        [ $? == 0 ] && ok_msg "${app_all_name} 应用在 ${app_ip} 上版本删除成功！"
    fi
}


# 解压上线应用
unzip_app(){
	local app_name=$1
	local app_addr=$2
	alarm_msg "开始解压位于: "${app_addr}"上的应用: "${app_name}
    # 开始解压应用
	ssh tomcat@${app_addr} "cd ~/release && /bin/tar xf ${app_name} -C /home/tomcat/release/"
	[[ $? == 0 ]] && ok_msg ${app_name}" To "${app_addr}": 应用解压完成!"
}

relink_app(){
	local app_name=$1
	local app_file=`echo ${app_name}|awk -F'.' '{print $1}'`
	local app=$2
	local app_addr=$3
	alarm_msg "删除位于主机:"${app_addr}" 应用:"${app}" 的link"
	# 删除link
	ssh tomcat@${app_addr} "rm -f /home/tomcat/${app}"
	if [[ $? != 0 ]];then
	    err_msg "删除失败，请检查！";exit 1
	fi
	#重新创建link
	ssh tomcat@${app_addr} "ln -s /home/tomcat/release/${app_file}  /home/tomcat/${app}"
	if [[ $? != 0 ]];then
	    err_msg "link创建失败，请检查！";exit 1
    fi
}

# 应用重启
restart_app(){
	local app_name=$1
	local app_addr=$2
	local app=`echo ${app_name}|awk -F'_' '{print $1}'`

	# 停止应用
	alarm_msg "位于主机："${app_addr}"的应用："${app}"，开始停机！！"
	ssh tomcat@${app_addr} "cd /home/tomcat/${app}/ && sh ./spring-boot.sh stop"
	if [[ $? != 0 ]];then
	    err_msg "应用停止异常，请检查！"
	fi
	# 更换应用超链接
	relink_app ${app_name} ${app} ${app_addr}
	[[ $? == 0 ]] && echo "新的link创建成功！"
	# 应用重启
	alarm_msg "位于主机："${app_addr}"的应用："${app}"，开始启动！！"
	ssh tomcat@${app_addr} "cd /home/tomcat/${app}/ && sh ./spring-boot.sh start"
	if [[ $? != 0 ]];then
	    err_msg "应用启动错误，请检查！"
	fi
}


# 读取列表下发应用
deploy(){
	typeset -l args
	args=$1
	if [[ "$args" == "help" ]]; then
		echo """
使用实例：
fabu.sh /tmp/deploy.txt

/home/manager/app/sx.txt:
recon-core_3455.gz
data-center-core_3456.gz
tarde-core_3457.gz
allpy-core_3458.gz
remit-core_3459.gz
注意事项：
1、manager家目录下的app文件夹内存放上线打包应用和sx.txt文件；
2、sx.txt文件内写着应用安装包全名，注意顺序
3、运行脚本即可
"""
		exit 1
	fi
	deploy_all_path=/home/manager/app/sx.txt
	alarm_msg $(echo "序号 应用名"|awk '{printf "%-15s%-20s\n",$1,$2}')
	alarm_msg "`cat ${deploy_all_path}|awk 'BEGIN{n=0;} {n=n+1; printf("%-15d%-20s\n",n,$0)}'`"
	time_signle=`/bin/date +%Y%m%d%H%M%S`
    new_bak_path="/home/manager/back/${time_signle}/"
	# 应用复制
	while read line ; do
		local app_name=${line}
		local app=`echo ${app_name}|awk -F'_' '{print $1}'`
		local app_path=/home/manager/app/${line}
		alarm_msg "开始复制应用： "${app_name}

        # 安装包检测
        if [[ ! -f ${app_path} ]];then
            # H5 检测
            if [[ ! -d ${app_path} ]];then
                err_msg "安装程序不存在:" ${app_path} "，请检查！"
                exit 1
            fi
        fi

		# 入口主机应用复制
		for i in ${input_app[@]}
		do
			if [[ "$i" == "${app}" ]];then
				for ip in ${input_addr[@]}
				do
					/usr/bin/scp -rp ${app_path} tomcat@${ip}:/home/tomcat/release/
					if [[ $? != 0 ]];then
					    err_msg ${app_name}" To "${ip}": 入口主机应用复制错误，请检查!"
					    exit 1
					fi
					unzip_app ${app_name} ${ip}
					restart_app ${app_name} ${ip}
					sign_version $(echo ${app_name}|awk -F'.' '{print $1}') ${ip}
					read -p "请按回车键继续！"
				done
			fi
		done

		# 运营主机应用复制
		for i in ${yycore_app[@]}
		do
			if [[ "$i" == "${app}" ]];then
				for ip in ${yycore_addr[@]}
				do
					/usr/bin/scp -rp ${app_path} tomcat@${ip}:/home/tomcat/release/
					if [[ $? != 0 ]];then
					    err_msg ${app_name}" To "${ip}": 运营应用复制错误，请检查!"
					    exit 1
					fi
					unzip_app ${app_name} ${ip}
					if [[ "${app}" == 'recon-core' ]] && [[ "${ip}" == '172.18.194.234' ]]; then
						continue
					else
					    restart_app ${app_name} ${ip}
					    sign_version $(echo ${app_name}|awk -F'.' '{print $1}') ${ip}
					    read -p "请按回车键继续！"
					fi
				done
			fi
		done

		# 交易主机应用复制
		for i in ${trade_app[@]}
		do
			if [[ "$i" == "${app}" ]];then
				for ip in ${trade_addr[@]}
				do
					/usr/bin/scp -rp ${app_path} tomcat@${ip}:/home/tomcat/release/
					if [[ $? != 0 ]];then
					    err_msg ${app_name}" To "${ip}": 交易主机应用复制错误，请检查!"
					    exit 1
					fi
					unzip_app ${app_name} ${ip}
					restart_app ${app_name} ${ip}
					sign_version $(echo ${app_name}|awk -F'.' '{print $1}') ${ip}
					read -p "请按回车键继续！"
				done
			fi
		done

		# 出口主机应用复制
		for i in ${out_app[@]}
		do
			if [[ "$i" == "${app}" ]];then
				for ip in ${out_addr[@]}
				do
					/usr/bin/scp -rp ${app_path} tomcat@${ip}:/home/tomcat/release/
					if [[ $? == 0 ]]; then
			            unzip_app ${app_name} ${ip}
					    restart_app ${app_name} ${ip}
					    sign_version $(echo ${app_name}|awk -F'.' '{print $1}') ${ip}
                        read -p "请按回车键继续！"
					else
					    err_msg ${app_name}" To "${ip}": 出口主机应用复制错误，请检查!"
					    exit 1
					fi
				done
			fi
		done

		# H5发布,H5 发布只需要将应用复制过去即可
        if [[ "${app_name}" == "app-ally" ]] || [[ "${app_name}" == "app-managent" ]];then
            while read ipline; do
                # 备份应用
                ssh tomcat@${ipline} "mv /home/tomcat/nginx/html/${app_name} /home/tomcat/release/${app_name}_${time_signle}"
                # 复制应用
                /usr/bin/scp -rp ${app_path} tomcat@${ipline}:/home/tomcat/nginx/html
                if [[ $? != 0 ]];then
                    err_msg "${app_name} 应用复制错误，请检查！"
                    exit 1
                fi
                ok_msg "节点:${ipline},H5应用：${app_name} 部署完成！"
                # 清理旧版本
                sign_version ${app_name}_${time_signle} ${ipline}
                # 完成
            done < `echo ${input_addr}|sed 's/\( \)\+/\n/g'`
        fi

		# 一个应用升级完成后，将安装包移走
		input_cmd="Swimming--->"
		read -p "是否备份此应用安装包，应用安装包迁移至back目录。【yes/no】"  input_cmd

		if [[ "${input_cmd}" == "yes" ]]; then
		    mkdir -p ${new_bak_path}
		    mv ${app_path} ${new_bak_path}
		else
		    err_msg "请注意！如果此应用下次不再需要上线，请手动删除app内安装包和sx.txt内的记录！！！"
		fi

	done < deploy_all_path
}

# 读取需要上线的应用列表 read_deploy file_path 应用上线格式文件夹
deploy $1| tee /home/manager/logs/deploy.log