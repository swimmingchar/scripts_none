#!/bin/bash
#放在定时内，通过定时触发
#version:1.1
#Time:2018/3/15
#最终使用版本，Del文件功能有问题，可以生成文件，单是删除有问题。
export LANG=en_US.utf-8
log_path="/var/tmp/script"

untar_main(){
	untar_list_path="/home/tomcat/Upload"
	unzip_path="/opt/catlogs/all"
	#tar_path="/backup/logbak"
	tar_path="/backup/typeback"
	tar_path_year=`date +%Y`
	tar_path_month=`date +%m`
	#日志存留时间
	del_date=`date -d '7 days ago' +%Y%m%d`
	del_date_d=`date -d '7 days ago' +%d`
	#解压密码
	unzip_pass="HzYb?2016"
	#中转文件，用于存放解压中间数据，最后可删除
	file_tmp=${log_path}/logs/temp_`date +%Y%m%d%s`.list
	test -f ${file_tmp} && cat /dev/null > ${file_tmp}
	#删除文件列表--需要确定有没有一个文件传给我两次的情况
	del_list=${log_path}/logs/del_`date +%Y%m%d%s`.list
	test -f ${del_list} && cat /dev/null > ${del_list}
	#一天汇总删除文件列表
	del_list_all=${log_path}/logs/all_del_`date +%Y%m%d%s`.list
	#test -f ${del_list_all} && cat /dev/null > ${del_list_all}
	#错误日志
	err_list=${log_path}/logs/err_`date +%Y%m%d%s`.list
	test -f ${err_list} && cat /dev/null > ${err_list}

	untar_sign=${untar_list_path}/.untar

	#检验是否再解压中
	test -f ${untar_sign} && echo -e "\n 解压中。。。。" && exit 0

	#检测文件数量
	untar_num=`/bin/ls -1 ${untar_list_path}|wc -l`
	if [[ ${untar_num} -eq 0 ]]; then
		echo -e "\n 没有检测到推送文件！"
		exit 0
	else
		#生成运行占用文件untar_sign
		/bin/ls -1 ${untar_list_path} > ${untar_sign}
	fi

	#开始解析文件
	for untar_file in `cat ${untar_sign}`; do
		#解压时间戳
		untar_time=`echo ${untar_file}|awk -F_ {'print $1'}`
		echo -e "解析文件："${untar_file}" 开始！\n\n"
		#读取文件
		while read line ; do
			#获取是否解压key
			untar_app_sign=`echo ${line}| awk -F: {'print $17'}`
			untar_app_name=`echo ${line}| awk -F: {'print $4'}`
			untar_app_ip=`echo ${line}| awk -F: {'print $5'}|awk -F. {'print $3"."$4'}`
			untar_full_path=${tar_path}/${tar_path_year}/${tar_path_month}/${untar_app_name}/${untar_app_ip}/${untar_app_name}_${untar_time}.tar.gz

			echo -e ${line}"行解析开始！\n\n"

			if [[ ${untar_app_sign} == "校验成功" ]]; then
				if [[ -f ${untar_full_path} ]]; then
					#创建新文件夹目录
					test -d ${unzip_path}/${untar_app_name}/${untar_app_ip} || mkdir -p ${unzip_path}/${untar_app_name}/${untar_app_ip}

					#第一次解压
					/usr/bin/openssl enc -d -des3 -k ${unzip_pass} -in ${untar_full_path} | tar -xv -C ${unzip_path}/${untar_app_name}/${untar_app_ip}

					#第二次解压
					[ $? ] && /bin/gzip -d ${unzip_path}/${untar_app_name}/${untar_app_ip}/*.gz || echo -e "第一次解压错误！" && exit 0

					# 生成删除列表
					cd ${unzip_path}/${untar_app_name}/${untar_app_ip}
					if [[ $? ]];then
						ls -lh| awk '$7==${day}' day=${del_date_d}|awk {'print $NF'} >${file_tmp}
						#生成删除列表，临时文件是否空
						while read del_line ;do
							# new_file=`echo ${del_line}|cut -d/ -f 2| awk -F.gz {'print $1'}`
							del_file_name=${unzip_path}/${untar_app_name}/${untar_app_ip}/${del_line}
							[ -f ${del_file_name} ] && echo -e ${del_file_name} |tee -a ${del_list}
						done < ${file_tmp}
					fi
				else
					echo ${untar_full_path}" is not in! at "`date +%H:%M:%S`!\n
				fi
			else
				echo -e "\n" ${untar_app_name}-${untar_app_ip} " 校验不通过，已跳过！"
			fi

		done < ${untar_list_path}/${untar_file}

		#备份解压完成文件
		test -d ${untar_list_path}/.bak || mkdir -p ${untar_list_path}/.bak
		mv ${untar_list_path}/${untar_file} ${untar_list_path}/.bak/
		[ $? ] && echo -e "\n文件":${untar_list_path}/${untar_file}" 已备份!"
	done

	# 删除文件
	test -f ${del_list_all} && echo -e "\n 删除列表已生成！" && exit 0
	# 没有删除列表时执行
	del_all_day_file_list=`find ${log_path}/logs -name "del_${del_date}*.list" `

	if [[ "" != "${del_all_day_file_list}" ]]; then
		# 汇总删除文件列表至删除list
		for i in ${del_all_day_file_list}; do
			cat $i >> ${del_list_all}
		done

		while read del_filename ; do
			test -f ${del_filename} && rm ${del_filename} && echo -e "rm "${del_filename}"\n"${del_filename}" delete success! at `date +%H:%M:%S`\n" || echo -e ${del_filename}" delete fail! at `date +%H:%M:%S`\n">>${err_list}
		done < ${del_list_all}
	else
		echo -e "no file need delete on "${unzip_date}
	fi

	#临时文件删除
	#test -f ${file_tmp} && rm ${file_tmp}
	#删除标记文件
	test -f ${untar_sign} && rm ${untar_sign}
	[ $? ] && echo -e  ${untar_sign}" 删除标记文件成功！"
}

untar_main 1>& ${log_path}/logs/`date +%s`.log