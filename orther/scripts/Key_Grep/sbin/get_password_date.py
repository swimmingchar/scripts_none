#!/usr/bin/env python
# -*- coding:utf-8 -*-
## 只能在root下使用
import spwd, sys

if spwd.getspnam(sys.argv[1]).sp_max < int(sys.argv[2]):
    return spwd.getspnam(sys.argv[1])
else:
    return 0
