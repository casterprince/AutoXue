#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: AutoXue
@file: config.py
@author: kessil
@contact: https://github.com/kessil/AutoXue/
@time: 2019-08-22(星期四) 16:59
@Copyright © 2019. All rights reserved.
'''

from configparser import ConfigParser
from pathlib import Path

cfg = ConfigParser()
cfg.read('./xuexi/config/default.ini', encoding='utf-8')
cfg.read('./xuexi/config/custom.ini', encoding='utf-8')


# xpath规则都是str类型，且频繁使用，将其单独列出
rules = {}
for option in cfg.options('rules'):
    rules.setdefault(option, cfg.get('rules', option))
