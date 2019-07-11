#!/usr/bin/env python
# -*- coding:utf-8 -*-

import redis
import time

# pool = redis.ConnectionPool(host='172.10.1.31', port=6379, db=0,password="")
# r = redis.Redis(connection_pool=pool)
r = redis.Redis(host='x.x.x.x', port=6379,db=0)


for item in r.scan_iter(count=10000):
    redis_ttl = r.ttl(item)
    if redis_ttl is None:
        # with open('/tmp/redis_key', 'w+') as f:
            # f.write(item)
        print(item)


