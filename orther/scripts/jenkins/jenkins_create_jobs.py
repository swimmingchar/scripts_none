#!/usr/bin/env python
# -*- coding:utf-8 -*-
import jenkins

template_xml="config.xml"
#server = jenkins.Jenkins('http://10.10.10.25:8080/', username='admin', password='shiweiming')
server = jenkins.Jenkins('http://172.10.1.31:8080/', username='admin', password='admin')
# jenkins admin token:   11b3f6d05fb4095465a3d2f7d17d5da3be
mode_file="/opt/cmsops/orther/scripts/jenkins/all-app.txt"


with open(mode_file,'r') as m_file:
    for app_line in m_file.readlines():
        project = app_line.split(",")[0]

        #for spider_name, crontab in job_list.items():
        with open(template_xml) as f:
            profile = f.read()
        # 支持2个IP
        ip1 = ""
        ip2 = ""
        app_ip = app_line.split(",")[2].split(";")
        if len(app_ip) == 1:
            ip1 = "<string>" + app_ip[0] + "</string>"
        elif len(app_ip) == 2:
            ip1 = "<string>" + app_ip[0] + "</string>"
            ip2 = "<string>" + app_ip[1] + "</string>"
        # svn
        svn_path = app_line.split(",")[3]
        # redis && add redis_node
        redis_path_job = ""
        try:
            redis_path = app_line.split(",")[1]
            r_node = redis_path.strip() + ".dat"
            if len(redis_path.strip()) != 0:
                redis_node_job = """
      <hudson.scm.SubversionSCM_-ModuleLocation>
        <remote>https://123.124.17.124:8443/repos/profile/proc/redis-node/""" + redis_path + """</remote>
        <credentialsId>c198ab7e-21e7-4e05-96bf-b3fb7301bf9b</credentialsId>
        <local>redis</local>
        <depthOption>infinity</depthOption>
        <ignoreExternalsOption>true</ignoreExternalsOption>
        <cancelProcessOnExternalsFail>true</cancelProcessOnExternalsFail>
      </hudson.scm.SubversionSCM_-ModuleLocation>"""
                redis_path_job = """
      <hudson.scm.SubversionSCM_-ModuleLocation>
        <remote>https://123.124.17.124:8443/repos/profile/auth-conf/""" + redis_path + """</remote>
        <credentialsId>c198ab7e-21e7-4e05-96bf-b3fb7301bf9b</credentialsId>
        <local>auth/redis</local>
        <depthOption>infinity</depthOption>
        <ignoreExternalsOption>true</ignoreExternalsOption>
        <cancelProcessOnExternalsFail>true</cancelProcessOnExternalsFail>
      </hudson.scm.SubversionSCM_-ModuleLocation>"""
        except Exception as msg:
            redis_path_job = ""
            print("%s 应用没有redis资源" %project)
        # 数据库
        db_path_job = ""
        try:
            db_path = app_line.split(",")[5]
            if len(db_path.strip()) != 0:
                db_path_job = """
      <hudson.scm.SubversionSCM_-ModuleLocation>
        <remote>https://123.124.17.124:8443/repos/profile/auth-conf/""" + db_path + """</remote>
        <credentialsId>c198ab7e-21e7-4e05-96bf-b3fb7301bf9b</credentialsId>
        <local>auth/db</local>
        <depthOption>infinity</depthOption>
        <ignoreExternalsOption>true</ignoreExternalsOption>
        <cancelProcessOnExternalsFail>true</cancelProcessOnExternalsFail>
      </hudson.scm.SubversionSCM_-ModuleLocation>"""
        except Exception as msg:
            db_path_job = ""
            print("%s 应用没有数据库资源" %project)
        # FTP
        ftp_path_job = ""
        try:
            ftp_path = app_line.split(",")[6]
            if len(ftp_path.strip()) != 0:
                ftp_path_job = """
      <hudson.scm.SubversionSCM_-ModuleLocation>
        <remote>https://123.124.17.124:8443/repos/profile/auth-conf/""" + ftp_path + """</remote>
        <credentialsId>c198ab7e-21e7-4e05-96bf-b3fb7301bf9b</credentialsId>
        <local>auth/ftp</local>
        <depthOption>infinity</depthOption>
        <ignoreExternalsOption>true</ignoreExternalsOption>
        <cancelProcessOnExternalsFail>true</cancelProcessOnExternalsFail>
      </hudson.scm.SubversionSCM_-ModuleLocation>"""
        except Exception as msg:
            ftp_path_job = ""
            print("%s 应用没有FTP资源" %project)
        dotwar = "jar"
        if project.strip() == "cas":
            dotwar = "war"

        JOB_CONFIG=profile.replace("app_name", project)\
            .replace("ip1", ip1)\
            .replace("ip2", ip2)\
            .replace("svn_path", svn_path)\
            .replace("auth_redis", redis_path_job)\
            .replace("auth_db", db_path_job)\
            .replace("jar", dotwar)\
            .replace("auth_ftp", ftp_path_job)

        #print(JOB_CONFIG[-200:])
        view_name = "{}_{}_".format(project, type)
        try:
            server.delete_job(project)
        except Exception as msg:
            print("%s is also delet"%project)
            #server.delete_job(project)
        server.create_job(project, JOB_CONFIG)