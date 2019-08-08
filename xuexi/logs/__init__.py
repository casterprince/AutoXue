#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: logs
@file: __init__.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-07-30(星期二) 17:52
@Copyright © 2019. All rights reserved.
'''
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# print(basedir)
levels = {
    'NOTSET': logging.NOTSET,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def create_logger(loggername:str='logger', levelname:str='NOSET'):
    filename = 'logger.log'
    logger = logging.getLogger(loggername)
    logger.setLevel(levels[levelname])

    logger_format = logging.Formatter("[%(asctime)s][%(levelname)s][%(filename)s][%(funcName)s][%(lineno)03s]: %(message)s")
    console_format = logging.Formatter("%(message)s")

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(console_format)
    handler_console.setLevel(logging.INFO)

    now = time.strftime("%Y%m%d")
    common_filename = f'{now}.log'
    handler_common = logging.FileHandler(os.path.join(basedir, 'LOG', common_filename), mode='a', encoding='utf-8')
    handler_common.setLevel(logging.DEBUG)
    handler_common.setFormatter(logger_format)

    handler_debug = TimedRotatingFileHandler(os.path.join(basedir, 'DEBUG', filename), encoding='utf-8', when='D', interval=1, backupCount=7)
    handler_debug.suffix = "%Y-%m-%d.log"  # "%Y-%m-%d_%H-%M-%S.log"
    handler_debug.setFormatter(logger_format)
    handler_debug.setLevel(logging.DEBUG)
    filter_debug = logging.Filter()
    filter_debug.filter = lambda record: record.levelno == logging.DEBUG
    handler_debug.addFilter(filter_debug)

    handler_info = TimedRotatingFileHandler(os.path.join(basedir, 'INFO', filename), encoding='utf-8', when='D', interval=1, backupCount=7)
    handler_info.suffix = "%Y-%m-%d.log"  # "%Y-%m-%d_%H-%M-%S.log"
    handler_info.setFormatter(logger_format)
    handler_info.setLevel(logging.INFO)
    filter_info = logging.Filter()
    filter_info.filter = lambda record: record.levelno == logging.INFO
    handler_info.addFilter(filter_info)

    handler_warning = TimedRotatingFileHandler(os.path.join(basedir, 'WARNING', filename), encoding='utf-8', when='D', interval=1, backupCount=7)
    handler_warning.suffix = "%Y-%m-%d.log"  # "%Y-%m-%d_%H-%M-%S.log"
    handler_warning.setFormatter(logger_format)
    handler_warning.setLevel(logging.WARNING)
    filter_warning = logging.Filter()
    filter_warning.filter = lambda record: record.levelno == logging.WARNING
    handler_warning.addFilter(filter_warning)

    handler_error = TimedRotatingFileHandler(os.path.join(basedir, 'ERROR', filename), encoding='utf-8', when='D', interval=1, backupCount=7)
    handler_error.suffix = "%Y-%m-%d.log"  # "%Y-%m-%d_%H-%M-%S.log"
    handler_error.setFormatter(logger_format)
    handler_error.setLevel(logging.ERROR)
    filter_error = logging.Filter()
    filter_error.filter = lambda record: record.levelno == logging.ERROR
    handler_error.addFilter(filter_error)

    handler_critical = TimedRotatingFileHandler(os.path.join(basedir, 'CRITICAL', filename), encoding='utf-8', when='D', interval=1, backupCount=7)
    handler_critical.suffix = "%Y-%m-%d.log"  # "%Y-%m-%d_%H-%M-%S.log"
    handler_critical.setFormatter(logger_format)
    handler_critical.setLevel(logging.CRITICAL)
    filter_critical = logging.Filter()
    filter_critical.filter = lambda record: record.levelno == logging.CRITICAL
    handler_critical.addFilter(filter_critical)

    logger.addHandler(handler_console)
    logger.addHandler(handler_common)
    # logger.addHandler(handler_debug)
    # logger.addHandler(handler_info)
    # logger.addHandler(handler_warning)
    # logger.addHandler(handler_error)
    # logger.addHandler(handler_critical)

    return logger

# logger = create_logger('logger', 'DEBUG')