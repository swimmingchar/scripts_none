#!/bin/bash

user_name=`whoami`
if [ "${user_name}"  == "tomcat" ];then
    end_year=`chage -l ${user_name} | head -2| tail -1 | awk -F: '{print $2}'| awk -F',' '{print $2}'| awk '{print $1}'`
    if [ "${end_year}" == "" ];then
        exit 0
    fi

    end_mounth=`chage -l ${user_name} | head -2| tail -1 | awk -F: '{print $2}'| awk -F',' '{print $1}'| awk '{print $1}'`

    case ${end_mounth} in
        'Jan') end_mounth=1;;
        'Feb') end_mounth=2;;
        'Mar') end_mounth=3;;
        'Apr') end_mounth=4;;
        'May') end_mounth=5;;
        'Jun') end_mounth=6;;
        'Jul') end_mounth=7;;
        'Aug') end_mounth=8;;
        'Sep') end_mounth=9;;
        'Oct') end_mounth=10;;
        'Nov') end_mounth=11;;
        'Dec') end_mounth=12;;
    esac

    end_day=`chage -l ${user_name} | head -2| tail -1 | awk -F: '{print $2}'| awk -F',' '{print $1}'| awk '{print $2}'`
    end_date_s=`/bin/date -d "${end_year}"-"${end_mounth}"-"${end_day}" +%s`
    star_date_s=`/bin/date +%s`
    let diffday=(${end_date_s}-${star_date_s})/86400
    echo ${diffday}>/tmp/user_expire_date
fi