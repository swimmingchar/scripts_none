#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pexpect
import sys

def ssh_cmd(ip):
    key_list = dict()
    with open("passw_key.list","rb") as f:
        for line in f.readlines():
            if line.split(":")[0].strip() == "old":
                key_list["passwd"] = line.split(":")[1].strip()
            if line.split(":")[0].strip() == "manager":
                key_list["new_passwd"] = line.split(":")[1].strip()
            if line.split(":")[0].strip() == "shiwm":
                key_list["shiwm_passwd"] = line.split(":")[1].strip()
            if line.split(":")[0].strip() == "tomcat":
                key_list["tomcat_passwd"] = line.split(":")[1].strip()
            if line.split(":")[0].strip() == "admin":
                key_list["admin_passwd"] = line.split(":")[1].strip()
            if line.split(":")[0].strip() == "kafka":
                key_list["kafka_passwd"] = line.split(":")[1].strip()
            if line.split(":")[0].strip() == "nginx":
                key_list["nginx_passwd"] = line.split(":")[1].strip()
            if line.split(":")[0].strip() == "redis":
                key_list["redis_passwd"] = line.split(":")[1].strip()

    ssh = pexpect.spawn('ssh manager@%s'%ip)

    try:
        i = ssh.expect(['UNIX password:'], timeout=1)
        i = ssh.expect(['UNIX password:'], timeout=1)
        if i == 0:
            ssh.sendline(key_list["passwd"])
            ssh.sendline("\n")
            ssh.sendline(key_list["new_passwd"])
            ssh.sendline("\n")
            ssh.sendline(key_list["new_passwd"])
            ssh.sendline("\n")
            ssh.sendline("sudo -i")
            ssh.sendline("\n")
            ssh.sendline(key_list["new_passwd"])
            ssh.sendline("\n")

            for key_pass in key_list:
                if key_pass != "passwd" and key_pass != "new":
                    cmd = "echo \'" + key_list["key_pass"] + "\' | passwd --stdin "+ key_pass.split("_")[0]
                    ssh.sendline(cmd)
                    ssh.sendline("\n")
                    print("IP：%s is OK" % ip)
        elif i == 1:
            ssh.sendline('yes\n')
            ssh.expect('password: ')
            ssh.sendline(key_list["passwd"])
        ret = 0
    except pexpect.EOF:
        print ("EOF")
        ssh.close()
        ret = -1
    except pexpect.TIMEOUT:
        print ("IP: %s is TIMEOUT" % ip)
        ssh.close()
        ret = -2
    return ret

if __name__=="__main__":
    host_list = []
    if len(sys.argv) == 2:
        with open(sys.argv[1], "rb") as f:
            for ip in f.readlines():
                num = ssh_cmd(ip)
