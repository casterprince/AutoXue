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
import os
from configparser import ConfigParser
from pathlib import Path


cfg = ConfigParser()
cfg.read('./xuexi/config/default.ini', encoding='utf-8')
try:
    CONFIG_PATH = os.environ['CONFIG_PATH'] or './xuexi/config/custom.ini'
except Exception:
    raise ValueError
finally:
    cfg.read(CONFIG_PATH, encoding='utf-8')

if __name__ == "__main__":
    for section in cfg.sections():
        print(f'\n[{section}]')
        for option in cfg.options(section):
            print(f'{option} = {cfg.get(section, option)}')





