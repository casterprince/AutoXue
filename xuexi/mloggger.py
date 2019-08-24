#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: AutoXue
@file: logger.py
@author: kessil
@contact: https://github.com/kessil/AutoXue/
@time: 2019-08-22(星期四) 17:34
@Copyright © 2019. All rights reserved.
'''

import time
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from .mconfig import cfg

def create_logger():
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

logger = create_logger()