#!/bin/bash

svn_cpmain(){
    back_date=`date +%Y%m%d%H`
    remote_path="/tmp/svnrepo_${back_date}"
    local_path="/home/svn/svnrepo"
    rsync_pwd="/var/tmp/script/pwd"
    sorce="/home/svn/svnrepo"
    dest="/opt/svnbak/svn_db/svnrepoback"

    /bin/ps -ef | grep svnserve | grep -v grep | awk '{print $2}'| xargs -I {} kill -9 {}
    test -d ${local_path} && /bin/rm -rf ${local_path}
    [ $? ] && /usr/bin/scp -rp root@10.63.9.198:${remote_path} ${local_path}
    cd ${local_path}
    find /home/svn/svnrepo/  -type f > /tmp/file_list.tmp
    awk -F"/home/svn/svnrepo" '{print $2}' /tmp/file_list.tmp > /tmp/file.list
    echo `date` >/tmp/copy_file.log
    while read line
    do
        md1=`/usr/bin/md5sum ${sorce}${line} | awk '{print $1}'`
        # 判断文件是否存在，如果不存在的话，判断上级目录是否存在，不存在创建目录
        if [ -f "${dest}${line}" ];then
            md2=`/usr/bin/md5sum ${dest}${line} | awk '{print $1}'`
        else
            md2="asddsfdsf"
            newfile=`/usr/bin/dirname ${dest}${line}`
            test -d ${newfile} || mkdir -p ${newfile}
        fi
        
        if [ ${md1} != ${md2} ];then
            echo "copy ${sorce}${line} to  ${dest}${line}" >>/tmp/copy_file.log
            scp -rp ${sorce}${line} ${dest}${line} 2>>/tmp/copy_file.log
        fi
    done < /tmp/file.list

    echo `date` >>/tmp/copy_file.log
    [ $? ] && /usr/local/svn/bin/svnserve -d -r ${local_path}
    
    # send mail
    echo "冷备开始时间：" `/usr/bin/head -1 /tmp/copy_file.log` > /tmp/temp.log
    echo "冷备结束时间：" `/usr/bin/tail -1 /tmp/copy_file.log` >> /tmp/temp.log
    echo '热备份svn最新日志【/home/svn/svnrepo/】：' >> /tmp/temp.log
    /usr/local/svn/bin/svn log file:///home/svn/svnrepo/ | head -2 >> /tmp/temp.log
    echo "" >> /tmp/temp.log
    echo '冷备份svn最新日志【/opt/svnbak/svn_db/svnrepoback/】：' >>/tmp/temp.log
    /usr/local/svn/bin/svn log file:///opt/svnbak/svn_db/svnrepoback/ | head -2 >>/tmp/temp.log
    echo 'SVN备份已完成。' >>/tmp/temp.log
    svnrsync_data=`cat /tmp/temp.log`

    #cat /tmp/temp.log | mutt -s "SVN同步-${back_date}" shiwm@test.com
    /var/tmp/script/xmail.py "shiwm@test.com" "SVN同步-${back_date}" ${svnrsync_data} "By 9.199."

}

svn_cpmain | tee -a /tmp/svn_rsync.log
