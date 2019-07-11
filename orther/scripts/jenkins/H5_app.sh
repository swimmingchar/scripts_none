#!/usr/bin/env bash
# 获取IP和版本号，用于部署，以及清理版本数量

function main() {
    app_ip=$1
    # H5 app Name
    h5_app=$3
    # 历史版本保留个数
    hold_back_ver=3
    # 版本发布真实地址
    remote_path=/home/tomcat/release/

    if [[ "$2" == "rollback" ]]; then
        # 回滚版本号
        h5_last_ver=$(/usr/bin/ssh -n tomcat@${app_ip} ls -1rt ${remote_path}| grep ${h5_app} |/usr/bin/tail -1)
        echo "回滚版本号：${h5_last_ver}"
        if [[ -n ${h5_last_ver} ]]; then
            # 清理当前版本
            echo "删除H5项目 ${h5_app} 应用。。。。"
            /usr/bin/ssh -n tomcat@${app_ip} rm -rf /home/tomcat/nginx/html/${h5_app}/*
            # 恢复旧版本号连接
            /usr/bin/ssh -n tomcat@${app_ip} cp -rp ${remote_path}${h5_last_ver}/* /home/tomcat/nginx/html/${h5_app}/
            echo -e "恢复上一次版本连接\n"$(/usr/bin/ssh -n tomcat@${app_ip} ls -ld /home/tomcat/nginx/html/${h5_app})
        else
            echo "获取版本不正确,最后一次版本号：${h5_last_ver}!"
            exit 1
        fi
    fi
    # 获取远端存留版本数
    version_num=$(/usr/bin/ssh -n tomcat@${app_ip} ls -1rt ${remote_path}| grep ${h5_app}| /usr/bin/wc -l)
    # 防止历史版本太少
    if [[ ${version_num} -lt 4 ]]; then
        echo "历史版本不需要清理!"
        exit 0
    fi
    # 根据保留数获取需要删除的版本号
    del_version=$(/usr/bin/ssh -n tomcat@${app_ip} ls -1rt ${remote_path}| grep ${h5_app}| /usr/bin/head -$(/usr/bin/expr ${version_num} - ${hold_back_ver}))

    # 防止空版本号循环误删
    if [[ -z ${del_version} ]]; then
        echo "没有需要清理的版本！"
        exit 0
    fi

    # 删除历史版本
    echo "|------->开始清理历史版本。。。"
    for app_ver in ${del_version[@]}
    do
        /usr/bin/ssh -n tomcat@${app_ip} "[[ -d "${remote_path}${app_ver}" ]] && rm -rf ${remote_path}${app_ver}"
        [[ $? == 0 ]] && echo "应用版本 ${app_ver} 清理完成..."
    done
    echo "------->|清理完成！"
}

# 调用方法: main ip clean/rollback
main $1 $2 $3