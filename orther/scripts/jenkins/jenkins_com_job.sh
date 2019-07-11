#!/bin/sh
# 脚本后面带项目名{$1}

USERNAME="admin"
PASSWORD="HzYb_20170328"
PRO_NAME=$1
SVN_ADDR_URL="https://123.124.17.124:8443/repos/profile/proc/"+${PRO_NAME}
PRO_WORKSPACE="/home/jenkins/workspace/"+${PRO_NAME}

INFO_URL=$(/usr/bin/svn info --username ${USERNAME} --password ${PASSWORD} ${SVN_ADDR_URL})

f [[ -z ${INFO_URL} ]]; then
    # ADDR 路径不存在处理
    echo "OK"
else
    # ADDR 路径存在处理
    # 切换至需要导出路径
    mkdir -p ${PRO_WORKSPACE}+"auth/addr/" && cd ${PRO_WORKSPACE}+"auth/addr/"
    /usr/bin/svn checkout ${SVN_ADDR_URL} ${PRO_WORKSPACE}+"auth/addr/"
fi


if [ ${DIFF_NUM} -ne 0 ]; then
    echo "different files ${DIFF_NUM}"
    DIFF_LIST=`${DIFF_URL}`
    NUM=0
    SKIP=0
    for FIELD in ${DIFF_LIST}; do
        if [ ${#FIELD} -lt 3 ]; then
            let NUM++
            SKIP=0
            if [ "${FIELD}" == "D" ]; then
                SKIP=1
            fi
            continue
        fi
        if [ ${SKIP} -eq 1 ]; then
            echo 'delete file, skip:'${FIELD}
            continue
        fi
        #变量替换
        DIFF_FILE=${FIELD//${SVN_URL}/}
        FILE_NAME=`basename ${DIFF_FILE}`
        FOLDER_NAME=`dirname ${DIFF_FILE}`
        FOLDER_PATH="${EXPORT_PATH}${FOLDER_NAME}"
        if [ ! -d "${FOLDER_PATH}" ]; then
            mkdir -p ${FOLDER_PATH}
        fi
        CMD="svn export -r ${NEW_VERSION} ${SVN_URL}${DIFF_FILE} ${FOLDER_PATH}/${FILE_NAME}"
        echo ${CMD}|sh
    done
fi