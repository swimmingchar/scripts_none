#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tty_menu import menu


menu_list = ['a','b','c']
pos = menu(menu_list, "你选择哪个？")
print("你的选择是：%s" %menu_list[pos])




#!/usr/bin/env python
# -*- coding:utf-8 -*-

import paramiko 
import sys, os 

mypath = os.path.dirname(os.path.realpath(__file__))

temp_key='ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA17jd4AwnL9zNXnTaZ2AAm7Dm1GbcT4kdTARCOoOxOB+IEFalLLXzB9d3GCO630D66JsTbMe1lAzH6mcFIyJZNGrRFDCsyy6igaktExK0ZAdTkbymBWEvr1bYcgYScLaukya5PIMawcd+gDWi6BPGxeIPR70SSndX3NjJwVBTJg36hB2wVkQNQmarJKNBnuTjc6pxkLuhHWGs2uFUTzWe6fxJeXTLNu2Gb8ZG076kxq3TTbXay/0KGtzjhBjVo4Rlq2Yku9AlN+hdXgNDwJOqMLuSbFM83vKV7l4pmS6nJJOqgbjpj2NYCOOBULjqONWBqT78oJKaAKBrpsZEnLclwQ== root@test03'

with open(mypath+"/.temp.key" , "w") as f:
    f.writelines(temp_key)
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='172.10.1.31', port=22,username='root',key_filename=mypath+"/.temp.key")
    stdin,stderr,stdout = ssh.exec_command('ls')
    res = stdout.read()
except expression as identifier:
    pass

ssh.close()




#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os , sys, time
import paramiko

if __name__ == "__main__":
    con_host=int(sys.argv[1])
    pra_key=sys.argv[2]
    
    mypath = os.path.dirname(os.path.realpath(__file__))

    with open(mypath + "/.temp.key", "w") as f:
        f.writelines(pra_key)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=con_host, port=22,username='root',key_filename=mypath+".temp.key")
        stdin,stdout,stderr = ssh.exec_command('touch /opt/swimming')
        res = stdout.read()
    except Exception as msg:
        print("error is %s"%msg)

    ssh.close()
        
