#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
# from fabric2 import ThreadingGroup as Group


# hosts=["swimming@192.168.50.200", "swimming@127.0.0.1"]
# host1 = ",".join(str(i) for i in hosts)
# print(host1)
# pool = Group(host1).run('uname -s')

# for i in pool.values():
#     print(i.connection.host)  
#     print(i.stdout
# # print(",".join(str(i) for i in hosts))

# for i in ["1","2","3","4"]:
#     if i =="2":
#         continue
#     print(i)

a = {"master":"70,76","slave":"10,12"}
b = json.dumps(a)
c = ",".join(str(i) for i in json.loads(b).values())
if "70" in c:
    print("OK")
print(",".join(str(i) for i in json.loads(b).values()))