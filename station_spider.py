#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/26 0026 19:18

import requests
import re
station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9056'
res = requests.get(station_url).text
res = re.findall(r"'(.*?)'", res)[0]
res = res.split('@')[1:]

content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/26 0026 19:18
station = {
"""
for item in res:
    temp = item.split('|')
    con = "    '%s': ['%s', '%s', '%s', '%s', '%s', %s]," % (temp[1], *temp) # * temp = >
                                               #  temp[0], temp[1],.. temp[-1]
    content = "%s\n%s" % (content, con)

content += '}'
with open('station.py', 'w', encoding='utf-8') as f:
    f.write(content)
