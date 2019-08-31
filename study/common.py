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
import time
import logging
from configparser import ConfigParser
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
pathdir = Path(__file__).parent / 'config'
def create_cfg():
    
    cfg = ConfigParser()
    cfg.read(str(pathdir / 'default.ini)', encoding='utf-8')
    cfg.read(str(pathdir / 'custom.ini'), encoding='utf-8')

    return cfg

def rules_to_dict(cfg):
    # xpath规则都是str类型，且频繁使用，将其单独列出
    rules = {}
    for option in cfg.options('rules'):
        rules.setdefault(option, cfg.get('rules', option))

    return rules

def new_custom_ini_while_not_exists():
    path = Path(str(pathdir / 'custom.ini'))
    if path.exists():
        # print(f'custom.ini 已存在')
        return False
    cfg = ConfigParser()
    cfg.read(str(pathdir / 'default.ini)', encoding='utf-8')
    with path.open(mode='w', encoding='utf-8') as fp:
        cfg.write(fp)
    print(f'用户配置文件 ./study/config.ini 已自动生成，请使用先进编辑器修改配置后重新运行')
    return True


def create_logger(cfg):
    logdir = Path(cfg.get('log_server', 'uri'))
    logdir.mkdir(parents=True, exist_ok=True)

    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    logger = logging.getLogger(cfg.get('log_server', 'name'))
    logger.setLevel(levels[cfg.get('log_server', 'log_level')])

    logger_format = logging.Formatter("[%(asctime)s][%(levelname)s][%(filename)s][%(funcName)s][%(lineno)03s]: %(message)s")
    console_format = logging.Formatter("[%(levelname)s] %(message)s")

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(console_format)
    handler_console.setLevel(levels[cfg.get('log_server', 'console_level')])

    now = time.strftime("%Y%m%d")
    common_filename = logdir / f'{now}.log'
    handler_common = logging.FileHandler(common_filename , mode='a+', encoding='utf-8')
    handler_common.setLevel(logging.DEBUG)
    handler_common.setFormatter(logger_format)

    logger.addHandler(handler_console)
    logger.addHandler(handler_common)

    return logger

class Timer:
    def __init__(self, func=time.perf_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError(f'Already started')
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError(f'Not Started')
        end = self._func()
        self.elapsed += end - self._start
        self._start = None

    def reset(self):
        self.elapsed = 0.0
    
    @property
    def running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

cfg = create_cfg()
rules = rules_to_dict(cfg)
logger = create_logger(cfg)

if __name__ == "__main__":
    new_custom_ini_while_not_exists()