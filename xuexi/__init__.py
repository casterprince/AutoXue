#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: __init__.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-08-02(星期五) 16:35
@Copyright © 2019. All rights reserved.
'''

from pathlib import Path
import re
from time import sleep
from configparser import ConfigParser
from .logs import create_logger


path = Path(__file__).parent
for item in ['json', 'xml', 'xls']:
    p = path/'src'/item
    p.mkdir(parents=True, exist_ok=True)
logger = create_logger('xuexi', 'DEBUG')
cfg = ConfigParser()
cfg.read(path/'config-default.ini', encoding='utf-8')
cfg.read(path/'config-custom.ini', encoding='utf-8')

class App(object):
    def __init__(self):
        self.rules = cfg.get('common', 'device')
        self.xmluri = Path(cfg.get(self.rules, 'xml_uri'))
        self.ad = adble.Adble(
                            self.xmluri,
                            cfg.getboolean(self.rules, 'is_virtual_machine'), 
                            cfg.get(self.rules, 'host'),
                            cfg.getint(self.rules, 'port'))
        self.xm = xmler.Xmler(self.xmluri)
        self.bonus = self._get_bonus()

    def _fresh(self):
        self.ad.uiautomator()
        self.xm.load()

    def _get_bonus(self):
        bonus = {}
        self._fresh()
        pos_mine = self.xm.pos(cfg.get(self.rules, 'rule_bottom_mine'))
        self.ad.tap(pos_mine)
        sleep(2)
        self._fresh()
        pos_bonus = self.xm.pos(cfg.get(self.rules, 'rule_bonus_entry'))
        self.ad.tap(pos_bonus)
        sleep(5)
        self._fresh()
        titles = self.xm.texts(cfg.get(self.rules, 'rule_bonus_title'))
        scores = self.xm.texts(cfg.get(self.rules, 'rule_bonus_score'))
        for title, score in zip(titles, scores):
            logger.info(f'{title} {score}')
            bonus.setdefault(title, score)
        self.ad.back()
        return bonus
        

    def _art_run(self):
        logger.debug(f'阅读文章,开始')
        rd = reader.Reader(self.rules, self.ad, self.xm)
        count = cfg.getint('common', 'article_count')
        delay = cfg.getint('common', 'article_delay')
        ssc = cfg.getint('common', 'star_share_comment')       # star_share_comment 收藏、分享、留言
        rd.run(count, delay, ssc)


    def _vdo_run(self):
        logger.debug(f'视听学习，开始')
        vd = viewer.Viewer(self.rules, self.ad, self.xm)
        count = cfg.getint('common', 'video_count')
        delay = cfg.getint('common', 'video_delay')
        vd.run(count, delay)

    def _quiz_run(self, day, chg):
        logger.debug(f'我要答题，开始')
        qApp = Quiz(self.rules, self.ad, self.xm)
        qApp.start(day, chg)

    def start(self):
        day = '已完成' != self.bonus['每日答题']
        chg = '已完成' != self.bonus['挑战答题']
        if day or chg:
            with timer.Timer() as t:
                self._quiz_run(day, chg)
            logger.info(f'答题耗时 {round(t.elapsed, 2)} 秒')
        
        vdo = '已完成' != self.bonus['视听学习'] or '已完成' != self.bonus['视听学习时长']
        if vdo:
            with timer.Timer() as t:
                self._vdo_run()
            logger.info(f'视听学习耗时 {round(t.elapsed, 2)} 秒')

        art = '已完成' != self.bonus['阅读文章'] or '已完成' != self.bonus['文章阅读时长']
        if art:
            with timer.Timer() as t:
                self._art_run()
            logger.info(f'文章阅读耗时 {round(t.elapsed, 2)} 秒')
        

    def __del__(self):
        self.ad.close()


    
        


from .common import adble, xmler, timer
from .model import Model
from .quiz import Quiz
from .media import viewer, reader