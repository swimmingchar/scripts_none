#!/bin/bash

err_msg(){
    echo -e "\033[31m\033[01m $1! \033[0m"
}

ok_msg(){
    echo -e "\033[1m\033[32m $1 \033[0m"
}

main(){
    node_home=`pwd`
    node_signle=`grep NODE_HOME ~/.bash_profile | wc -l`
    fe_path=`pwd`"/lib/node_modules/fe/bin/fe.js"
    if [ "${node_signle}" == "0" ];then
        sed -i '/^export* PATH$/d' ~/.bash_profile
        # node.js and pm2 env 
        echo "#NODE_HOME ENV and pm2 model for swimming" >> ~/.bash_profile
        echo "export NODE_HOME=${node_home}" >> ~/.bash_profile
        echo "export PM_HOME=${node_home}/lib/node_mode/pm2" >> ~/.bash_profile
        echo 'PATH=$PATH:$NODE_HOME/bin:$PM_HOME/bin' >> ~/.bash_profile
        echo "export PATH" >> ~/.bash_profile
        if [ $? == "0" ]; then
            ok_msg "初始化完成！"
            ok_msg "Plase run source ~/.bash_profile"
        else
            err_msg "执行脚本错误！"
            exit
        fi
    else
        err_msg "已添加环境变量，请确认NODE_HOME是否添加！"
    fi
}

main