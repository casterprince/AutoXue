#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: AutoXue
@file: app.py
@author: kessil
@contact: https://github.com/kessil/AutoXue/
@time: 2019-08-26(星期一) 22:26
@Copyright © 2019. All rights reserved.
'''
import os
import re
import json
import requests
import string
import time
from pathlib import Path
from urllib.parse import quote
from random import uniform, randint, choice
from itertools import accumulate
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .model import db, Bank
from .common import cfg, rules
from .common import logger as log
from .common import Timer

class Automation():
    # 初始化 appium_server 基本参数
    def __init__(self, wait_seconds):
        log.debug(f'打开 appium_server 服务器...')
        log.info(f'正在配置 appium_server ...')
        self.driver = webdriver.Remote(self.driver_server, self.desired_caps)
        self.wait = WebDriverWait(self.driver, wait_seconds, 1)
        self.size = self.driver.get_window_size()

    def __del__(self):
        try:
            self.driver.close_app()
        except:
            log.debug(f'还没有连接设备')

    def connect_device(self):
        pass

    def disconnect_device(self):
        pass

    # 屏幕方法
    def swipe_up(self):
        # 向上滑动屏幕
        self.driver.swipe(self.size['width'] * 0.5,
                          self.size['height'] * 0.85,
                          self.size['width'] * 0.5,
                          self.size['height'] * 0.15, uniform(800, 1200))
        log.debug(f'向上滑动屏幕')

    def swipe_down(self):
        # 向下滑动屏幕
        self.driver.swipe(self.size['width'] * 0.5,
                          self.size['height'] * 0.15,
                          self.size['width'] * 0.5,
                          self.size['height'] * 0.85, uniform(800, 1200))
        log.debug(f'向下滑动屏幕')

    def swipe_right(self):
        # 向左滑动屏幕
        self.driver.swipe(self.size['width'] * 0.8,
                          self.size['height'] * 0.5,
                          self.size['width'] * 0.2,
                          self.size['height'] * 0.5, uniform(800, 1200))
        log.debug(f'向左滑动屏幕')

    def swipe_left(self):
        # 向右滑动屏幕
        self.driver.swipe(self.size['width'] * 0.2,
                          self.size['height'] * 0.5,
                          self.size['width'] * 0.8,
                          self.size['height'] * 0.5, uniform(800, 1200))
        log.debug(f'向右滑动屏幕')

    def flick_up(self):
        # 快速向上滑动屏幕
        self.driver.flick(self.size['width'] * 0.5,
                          self.size['height'] * 0.8,
                          self.size['width'] * 0.5,
                          self.size['height'] * 0.3)
        log.debug(f'快速向上滑动屏幕')

    def click(self, rule):
        log.debug(f'clicking {rule}')
        ele = self.wait.until(EC.presence_of_element_located((By.XPATH, rule)))        
        ele.click()
        time.sleep(1)
        log.debug(f'contexts {self.driver.contexts}')

    def back(self):
        # https://blog.csdn.net/weixin_42082222/article/details/81298219
        log.debug(f'触发 KEY_CODE_BACK 事件 ...')
        self.driver.keyevent(4)
        

    def mute(self):
        log.debug(f'触发 KEYCODE_VOLUME_MUTE 事件 ...')
        self.driver.keyevent(164)
        # for i in range(10):
        #     self.driver.keyevent(25)
        #     time.sleep(1)

class Xuexi(Automation):
    def __init__(self):
        self.driver_server = cfg.get('appium_server', 'driver_server')
        self.desired_caps = {
            "platformName": cfg.get('appium_server', 'platform_name'),
            "platformVersion": cfg.get('appium_server', 'platform_version'),
            "deviceName": cfg.get('appium_server', 'device_name'),
            "uuid": cfg.get('appium_server', 'uuid'),
            'automationName': cfg.get('appium_server', 'automation_name'),
            "appPackage": cfg.get('appium_server', 'app_package'),
            "appActivity": cfg.get('appium_server', 'app_activity'),
            "unicodeKeyboard": cfg.get('appium_server', 'unicode_keyboard'),
            "resetKeyboard": cfg.get('appium_server', 'reset_keyboard'),
            "noReset": cfg.get('appium_server', 'no_reset'),
            "deviceReadyTimeout": cfg.getint('appium_server', 'device_ready_timeout')
        }
        wait_until_seconds = cfg.getint('appium_server', 'wait_until_seconds')
        super().__init__(wait_until_seconds)
        # 判断需要登录否
        self._login_or_not()
        # 初始化一个空白题
        self.catagory = ''
        self.content = ''
        self.options = []
        self.bank = None
        self.bonus = self._get_bonus()
        print()
        for title in ['阅读文章', '视听学习', '每日答题', '挑战答题']:
            obtain, total = self.bonus[title]
            print(f'\t{title} {obtain}/{total}', end='')
        print(f'\n')
        self.comments = self._load()

    def _load(self):
        path = Path(cfg.get('database_server', 'Staging'))
        if not path.exists():
            return []
        with path.open(mode='r', encoding='utf-8') as fp:
            data = json.load(fp)
        return data

    def _dump(self):
        path = Path(cfg.get('database_server', 'Staging'))
        with path.open(mode='w', encoding='utf-8') as fp:
            json.dump(self.json_bank, fp, indent=4, ensure_ascii=False)

    def _find_in_json_bank(self, content):
        res = None
        for item in self.json_bank:
            if content == item['content']:
                res = item
                break
        return res

    def _login_or_not(self):
        try:
            self.click(rules['work'])
            log.debug(f'无需重新登录')
        except:
            # login = self.driver.find_element_by_xpath(rules['btn_login'])
            edits = self.driver.find_elements_by_xpath(rules['username_password'])
            username, password = edits
            username.send_keys(cfg.get('secret', 'username'))
            password.send_keys(cfg.get('secret', 'password'))
            self.click(rules['btn_login'])
            time.sleep(10)
            self.click(rules['agree_protocol'])
            log.debug(f'正在登录 ...')
            time.sleep(5)

    def _get_bonus(self):
        log.debug(f'获取积分情况，根据积分情况执行相关动作')
        bonus = {}
        self.click(rules['mine'])
        self.click(rules['bonus_entry'])
        # titles = '登录 阅读文章 视听学习 文章学习时长 视听学习时长 每日答题 每周答题 专项答题 挑战答题 订阅 收藏 分享 发表观点'.split(' ')
        getting_bonus = True
        while getting_bonus:
            titles = [ele.get_attribute('name') for ele in self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['bonus_titles'])))]
            scores = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['bonus_nums'])))
            first_title = titles[0]
            for title, score in zip(titles, scores):
                res = score.get_attribute('name')
                obtain, total = [int(x) for x in re.findall(r'\d+', res)]
                bonus.setdefault(title, (obtain, total))
                log.debug(f'{title:8} {obtain}/{total} {("×", "√")[obtain == total]}')
                if '发表观点' == title:
                    getting_bonus = False
                    break
            else:
                self.driver.scroll(title, first_title, 1000)
        self.back()
        return bonus


    def _star_share_comment(self, title):
        try:
            edit_area = self.driver.find_element_by_xpath(rules['edit_area'])
            log.debug(f'这是一篇开启评论的文章')
        except Exception as e:
            edit_area = None
            log.debug(f'这是一篇关闭评论的文章\n{e}')
        if edit_area:
            log.debug(f'{title} Star Share Comment 三件套 ...')
            edit_area.click()
            comments_matched = False
            for item in self.comments:
                for tag in item['tags']:
                    if tag in title:
                        msg = choice(item['comments'])
                        comments_matched = True
                        break
                if comments_matched:
                    break
            else:
                msg = choice(self.comments[0]['comments'])
            # msg = '''不忘初心，牢记使命，高举中国特色社会主义伟大旗帜，决胜全面建成小康社会，夺取新时代中国特色社会主义伟大胜利，为实现中华民族伟大复兴的中国梦不懈奋斗。'''
            edit_input = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['edit_input'])))
            log.info(f'留言：{msg}')
            edit_input.send_keys(msg)
            self.click(rules['btn_comments_publish'])   # 点击发布按钮
            self.click(rules['btn_star'])               # 点击收藏按钮
            self.click(rules['btn_share'])              # 点击分享按钮
            self.click(rules['btn_share2xuexi'])        # 分享到學習强國
            self.back()                                 # 返回，放弃分享
            if not cfg.getboolean('prefer', 'keep_star_comments'):
                self.click(rules['btn_comments_delete'])            # 点击删除留言按钮
                self.click(rules['btn_comments_delete_confirm'])    # 点击确认删除按钮
                self.click(rules['btn_star'])                       # 点击取消收藏按钮
            return 1
        else:
            return 0

    def _read_article(self, title, delay, delay_unit:int=10):
        log.debug(f'阅读一篇新闻 {title}')
        for i in range(delay//delay_unit):
            time.sleep(delay_unit)
            self.swipe_up()

        # 新思路
        #   对于开放评论的文章，点击评论按钮将直接跳到文末
        #   对于关闭评论的文章，你都关闭评论了，我为什么要给你点赞
        try:
            comments = self.driver.find_element_by_xpath(rules['btn_comments'])
            log.debug(f'既然你开放了评论，我就给你点个赞吧，一场缘分')
            comments.click()
            time.sleep(1)
            like = self.driver.find_element_by_xpath(rules['thumb_up'])
            log.debug(f'location_in_view of like: {like.location_in_view}')
            like.click()
            time.sleep(2)
        except Exception as e:
            log.debug(f'{e}既然你关闭了评论，我就没办法给你点赞了，有缘无份')

        # 获取点赞元素位置之前应该让屏幕静止
        # 之前的想法太单纯，想着一直滑动屏幕直到thumb up出现
        # for i in range(5):
        #     time.sleep(2)
        #     try:
        #         like = self.driver.find_element_by_xpath(rules['thumb_up'])
        #         log.debug(f'location_in_view of like: {like.location_in_view}')
        #         like.click()
        #         log.debug(f'刷到你就是缘分，给你一个免费的赞👍')
        #         time.sleep(2)
        #         break
        #     except Exception as e:
        #         log.debug(e)
        #         log.debug(f'没有找到 like-wrapper')
        #         self.swipe_up()
        # else:
        #     log.debug(f'尝试了 5 次，实在找不到点赞按钮，放弃吧')

    def read(self, num:int, delay:int, ssc:int):
        log.debug(f'阅读文章 {num} 篇 {delay} 秒/篇')
        tab_name = cfg.get('prefer', 'column_of_news')
        finding_column = True
        self.click(rules['work'])
        while finding_column:
            columns = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['column_name'])))
            first_column = columns[0]
            for column in columns:
                column_name = column.get_attribute('name')
                log.debug(f'current {column_name} {column.location}, target {tab_name}')
                if tab_name == column_name:
                    column.click()
                    finding_column = False
                    break
            else:
                log.debug(f'没有找到栏目 {tab_name} 拖动一屏 ...')
                self.driver.scroll(column, first_column, 1000)
                # self.driver.swipe(column.location['x'], column.location['y'], first_column.location['x'], first_column.location['y'], 500)
        self.click(rules['work']) # 刷新
        readed_list = []
        while num > 0:
            # news = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['news_list'])))
            # fixed_top, fixed_bottom = news[0], news[-1]
            try:
                articles = self.driver.find_elements_by_xpath(rules['news_title'])
            except:
                articles = []
            for article in articles:                
                title = article.get_attribute('name')
                if title in readed_list:
                    continue
                num -= 1
                log.info(f'[{num}] {title}')
                article.click()
                self._read_article(title, delay)
                if ssc > 0:
                    ssc -= self._star_share_comment(title)
                self.back()
                readed_list.append(title)
                if 0 == num:
                    break
            else:
                self.swipe_up()
                # self.driver.scroll(fixed_bottom, fixed_top, 1000)
                # self.driver.swipe(fixed_bottom.location['x'], fixed_bottom.location['y'], 
                #                 fixed_top.location['x'], fixed_top.location['x'], 1000)
        else:
            log.debug(f'新闻学习完毕!')
        


            

    def view_videos(self, num:int, delay:int):
        log.debug(f'视听学习 百灵短视频 {num} 则 {delay} 秒/则')
        channel = cfg.get('prefer', 'column_of_video')
        rule = re.sub(r'default_channel', channel, rules['ding_channel'])
        self.click(rules['ding'])
        self.click(rule)
        self.click(rules['first_video'])
        while num > 0:
            num -= 1
            log.info(f'视听学习 百灵 第 {num} 则, 观看 {delay} 秒 ...')
            time.sleep(delay) # 程序运行太快，视频还没刷出来就上滑了，所以建议再给 5秒刷新时间
            # self.flick_up() # 太快了，模拟器承受不住
            self.swipe_up()
        else:
            log.info(f'视听学习完成')
            self.back()

    
    def view_newscast(self, delay):
        log.debug(f'视听学习 新闻联播 {delay} 秒')
        self.click(rules['contact'])
        self.click(rules['newscast_enter'])
        self.click(rules['first_video'])
        log.info(f'正在收看新闻联播 {delay} 秒 ...')
        time.sleep(delay)
        self.back()

    def bg_fm(self):
        ''' 如果视听学习时长未达标，进入APP先打开后台FM'''
        is_mute = cfg.getboolean('prefer', 'volume_mute')
        if is_mute:
            self.mute()
        channel = cfg.get('prefer', 'channel_of_fm')
        log.info(f'请不要介意我打开 FM {channel}')
        self.click(rules['contact'])
        self.click(rules['audiovisual_entry'])
        rule = re.sub(r'default_channel', channel, rules['fm_channel'])
        self.click(rule)
        time.sleep(3)
        # self.click(rules['work'])

    def quiz(self):
        ''' 0. click 學習（刷新）
            1. click 我的
            2. click 我要答题
            3. Callback: quiz_daily, quiz_weekly, quiz_monthly, quiz_challenge
            4. keyevent KEYCODE_BACK
        '''
        log.debug(f'我要答题')
        
        # step 0
        # self.click(rules['work'])
        # step 1
        self.click(rules['mine'])
        log.debug(f'contexts {self.driver.contexts}')
        time.sleep(2)
        self.click(rules['quiz_entry'])
        quiz_weekday = cfg.get('prefer', 'quiz_weekday')
        force_daily, force_challenge = 0, 0
        try:
            force_daily = int(os.environ.get('FORCE_DAILY'))
        except:
            log.debug(f'没有指定 FORCE_DAILY')
        try:
            force_challenge = int(os.environ.get('FORCE_CHALLENGE'))
        except:
            log.debug(f'没有指定 FORCE_CHALLENGE')
        log.debug(f'FORCE_DAILY: {force_daily}\tFORCE_CHALLENGE: {force_challenge}')

        delay = cfg.getint('prefer', 'delay_daily')
        daily_obtain, daily_total = self.bonus['每日答题']
        self.quiz_daily(obtain=daily_obtain, total=daily_total, delay=delay, force_daily=force_daily)

        challenge_obtain, challenge_total = self.bonus['挑战答题']
        if challenge_obtain == challenge_total:
            log.info(f'挑战答题已完成，跳过挑战答题')
        else:
            num = cfg.getint('prefer', 'count_challenge')
            delay = cfg.getint('prefer', 'delay_challenge')
            self.quiz_challenge(num, delay)
        if force_challenge > 0:
            log.debug(f'额外执行挑战 {force_challenge} 题')
            self.quiz_challenge(force_challenge)

        today_weekday = time.strftime("%A", time.localtime())
        if quiz_weekday == today_weekday:
            log.info(f'今天 {today_weekday}, 真是一个做每周答题和专项答题的好日子')
            weekly_obtain, _ = self.bonus['每周答题']
            if 0 == weekly_obtain:
                self.quiz_weekly()
            else:
                log.debug(f'每周答题已挑战，跳过每周答题')

            monthly_obtain, _ = self.bonus['专项答题']
            if 0 == monthly_obtain:
                self.quiz_monthly()
            else:
                log.debug(f'专项答题已挑战，跳过专项答题')
        else:
            log.debug(f'今天是 {today_weekday} 而不是 {quiz_weekday} 原谅我不做每周答题和专项答题')
        
        # 此时答题项目全部完成，是时候返回一步到首页去了
        self.back()

    def _split_str_by_tuple(self, source:str, edit_tuple:tuple)->str:
        if len(source) != sum(edit_tuple):
            raise ValueError(f'参考答案长度不匹配')
        s = list(source)
        lx = [x for x in accumulate(edit_tuple)]
        for i in lx[-2::-1]:
            s.insert(i, ' ')
        return ''.join(s)

    def _get_note(self, count_edits=1, each_edit:list=None)->bool:
        time.sleep(1)
        try:
            correct = self.driver.find_element_by_xpath(rules['correct'])
            log.debug(f'sorry, you did not choose the right answer')
        except:
            correct = None
            log.debug(f'congratulations, you did choose the right answer')
        if correct:
            answer = re.sub(r'正确答案：', '', correct.get_attribute('name'))
            log.info(f'正确答题 {answer}')
            note = self.driver.find_element_by_xpath(rules['note']).get_attribute('name') or ''
            toadd = Bank(catagory=self.catagory, content=self.content, options=self.options, answer=answer, note=note)
            if '填空题' == self.catagory:
                toadd.options = count_edits
            if count_edits > 1:
                # 通过一定处理，具备多项填空题存入数据库的条件了，哈哈哈~
                toadd.answer = self._split_str_by_tuple(answer, each_edit)
            db.add(toadd)
            return False
        else:
            if self.bank is None:
                toadd = Bank(catagory=self.catagory, content=self.content, options=self.options, answer=self.default_answer, note='')
                db.add(toadd)
            else:
                log.debug(f'题库存在，不用添加')
            return True

    def _solve_blank(self):
        log.debug(f'这是一道填空题 ...')
        self.options = []
        texts = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['content_blank'])))
        # log.debug(texts)
        self.content = " ".join([t.get_attribute('name').replace(u'\xa0', u' ') for t in texts])
        log.info(f'[填空题] {self.content}')
        if not self.content:
            raise RuntimeError(f'没有捕获到填空题题干 ...')     
        edits = self.driver.find_elements_by_xpath(rules['edit_text'])
        if len(edits) > 1:
            containers = self.driver.find_elements_by_xpath(rules['ecah_edit_length'])
            # 这是一个元组推导式，统计每个EditText的兄弟节点数量
            each_edit = [len(container.find_elements_by_class_name('android.view.View'))-1 for container in containers]
            log.debug(f'空格元组: {each_edit}')
        else:
            each_edit = None

        self.bank = db.query(content=self.content, catagory='填空题')
        self.options = str(len(edits))
        if self.bank is not None:
            log.info(f'自动提交答案 {self.bank.answer}')
            answers = self.bank.answer.split(' ')
            for edit, answer in zip(edits, answers):
                # edit.click()
                edit.send_keys(answer)
            else:
                self.click(rules['submit'])
        else:
            self.default_answer = '不忘初心牢记使命'
            log.info(f'默认提交答案 {self.default_answer}')
            for edit in edits:
                # edit.click()
                edit.send_keys(self.default_answer)
            else:
                self.click(rules['submit'])
        if not self._get_note(len(edits), each_edit=each_edit):
            # 答错了，点击 下一题
            self.click(rules['submit'])

    def _solve_radio(self):
        log.debug(f'这是一道单选题 ...')
        self.content = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['content_radio_check']))).get_attribute('name').replace(u'\xa0', u' ')
        log.info(f'[单选题] {self.content}')        
        if not self.content:
            raise RuntimeError(f'没有捕获到题干 ...')
        options = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['options_radio'])))
        self.options = [option.get_attribute('name').replace('|', ' ') for option in options]
        log.info(f'[选项] {self.options}')
        if not "".join(self.options):
            raise RuntimeError(f'没有捕获到选项')
        self.bank = db.query(content=self.content, catagory='单选题')
        if self.bank is not None:
            cursor = ord(self.bank.answer) - 65
            log.info(f'自动提交答案 {self.bank.answer}')
            options[cursor].click()
            self.click(rules['submit'])
        else: # 选最后一个
            self.default_answer = chr(len(options)+64)
            log.info(f'默认提交答案 {self.default_answer}')
            options[-1].click()
            self.click(rules['submit'])
        if not self._get_note():
            self.click(rules['submit'])

    def _solve_check(self):
        log.debug(f'这是一道多选题 ...')
        self.content = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['content_radio_check']))).get_attribute('name').replace(u'\xa0', u' ')
        log.info(f'[多选题] {self.content}')
        if not self.content:
            raise RuntimeError(f'没有捕获到题干 ...')
        options = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['options_check'])))
        self.options = [option.get_attribute('name').replace('|', ' ') for option in options]
        log.info(f'[选项] {self.options}')
        if not "".join(self.options):
            raise RuntimeError(f'没有捕获到选项')
        if not self.content:
            raise RuntimeError(f'没有捕获到题干 ...')
        self.bank = db.query(content=self.content, catagory='多选题')
        if self.bank is not None:
            log.info(f'自动提交答案 {self.bank.answer}')
            for option, answer in zip(options, ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']):
                if answer in self.bank.answer:
                    option.click()
            else:
                self.click(rules['submit'])
        else: # 全选
            self.default_answer = 'ABCDEFGHIJK'[0:len(self.options)]
            log.info(f'默认提交答案 {self.default_answer}')
            for option in options:
                option.click()
            else:
                self.click(rules['submit'])
        if not self._get_note():
            self.click(rules['submit'])

    def _dispatch(self):
        ''' 0. get catagory
            1. switch to sub func
            2. exit or again
        '''
        log.debug(f'开始分派 ...')
        self.note = ''
        self.bank = None
        self.catagory = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['catagory']))).get_attribute('name')
        if not self.catagory:
            raise RuntimeError(f'没有捕获到题目类型')
        # self.driver.find_element_by_xpath(rules['catagory']).get
        # log.debug(self.catagory)
        if '填空题' == self.catagory:
            self._solve_blank()
        elif '单选题' == self.catagory:
            self._solve_radio()
        elif '多选题' == self.catagory:
            self._solve_check()
        else:
            log.debug(f'未知的题目类型 {self.catagory}')
            raise RuntimeError(f'未知的题目类型 {self.catagory}')

    def quiz_daily(self, obtain, total, delay=3, force_daily=0):
        ''' 0. click 每日答题
            1. cycle 填空题、单选题、多选题
            2. score_reached? back: again
        '''        
        if total - obtain + force_daily == 0:
            log.info(f'每日答题已完成，跳过每日答题')
            return 
        log.info(f'每日答题 {delay} 秒/组 (force_daily | {force_daily})')
        self.click(rules['daily'])
        while True:
            for i in range(5):
                self._dispatch()
                time.sleep(1)

            # 通过计算得分情况作为结束标志
            score = int(self.wait.until(EC.presence_of_element_located((By.XPATH, rules['score']))).get_attribute('name'))
            obtain += score
            if obtain < total:
                log.info(f'每日答题积分{obtain}/{total},再来一组 ...')
                time.sleep(delay)
                self.click(rules['next'])
                continue
            else:
                log.info(f'每日答题积分{obtain}/{total},已达成')
                if 0 == force_daily:
                    log.debug(f'已完成指定的额外答题任务，返回')
                    self.click(rules['return'])
                    break
                else:
                    log.debug(f'指定的额外答题任务，还剩{force_daily}组，加油！')
                    force_daily -= 1
                    time.sleep(delay)
                    self.click(rules['next'])
                    continue

            # 通过 领取奖励已达今日上限 标识判定结束
            # time.sleep(3)
            # try:
            #     reached = self.driver.find_element_by_xpath(rules['score_reached'])
            #     if 0 == force_daily:
            #         log.info(f'已达成今日份每日答题，返回')
            #         self.click(rules['return'])
            #         break
            #     else:
            #         log.info(f'额外要求再来一组：第 {force_daily} 组, {delay} 秒后开始 ...')
            #         force_daily -= 1
            #         time.sleep(delay)
            #         self.click(rules['next'])
            #         continue 
            # except:
            #     log.info(f'未达到6分, {delay} 秒后再来一组 ...')
            #     time.sleep(delay)
            #     self.click(rules['next'])
            #     continue

    def quiz_weekly(self, auto=False):
        ''' 0. click 每周答题
        '''
        log.debug(f'每周答题')
        log.info(f'骚年你想太多了，每周答题都要用自动化')

    def quiz_monthly(self, auto=False):
        ''' 0. click 专项答题
        '''
        log.debug(f'专项答题')
        log.info(f'骚年你想太多了，专项答题都要用自动化')

    def _search(self, bank)->str:
        log.debug(f'正在问度娘')
        if self.options[-1].startswith(f'以上'):
            log.debug(f'最后一个选项可能性很大，不问度娘了')
            return chr(len(self.options)+64)        
        content = re.sub(r'[\(（]出题单位.*', "", self.content)
        url = quote('https://www.baidu.com/s?wd=' + content, safe=string.printable)
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        }
        response = requests.get(url, headers=headers).text
        counts = []
        for c, option in zip(['A', 'B', 'C', 'D'], self.options):
            count = response.count(option)
            counts.append((count,c))
            log.info(f' {c}. {option} : {count}')
        counts = sorted(counts, key=lambda x: x[0], reverse=True)
        if bank:
            for _, c in counts:
                if c not in bank.note:
                    return c
        else:
            _, answer = counts[0]
            return answer
                
    def quiz_challenge(self, num:int=30, delay:int=2):
        while self._quiz_challenge_round(num, delay):
            log.debug(f'没有达成 {num} 题, 再来一局')
        else:
            log.debug(f'挑战达成，哈哈哈')
          
    def _quiz_challenge_round(self, num:int=30, delay:int=2):
        ''' 0. click 挑战答题
            1. cycle 挑战题
            2. question_count_reached? back: again
        '''
        if delay <= 0 or delay > 5:
            delay = randint(1, 5)
        log.debug(f'挑战答题 {num} 题 延时提交 {delay} 秒/题')
        self.click(rules['challenge'])
        while num:
            log.debug(f'挑战答题 第 {num} 题')
            self.content = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['content_challenge']))).get_attribute('name').replace(u'\xa0', u' ')
            log.info(f'[挑战题 {num}] {self.content}')
            if not self.content:
                raise RuntimeError(f'没有捕获到挑战题 题干 ...')
            options = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['options_challenge'])))
            self.options = [o.get_attribute('name').replace('|', ' ') for o in options]
            log.info(f'[选项] {self.options}')
            if not "".join(self.options):
                raise RuntimeError(f'没有捕获到挑战题 选项')
            bank = db.query(content=self.content, catagory='挑战题')
            if bank and bank.answer:
                search_answer = bank.answer
                log.info(f'自动提交答案 {search_answer}')
            else:
                search_answer = self._search(bank)
                log.info(f'尝试提交答案 {search_answer}')
            options[ord(search_answer) - 65].click()
            time.sleep(3)
            try:
                stop_round = self.driver.find_element_by_xpath(rules['stop'])
                log.debug(f'回答错误')
                if not bank:
                    log.debug(f'新增一题: 含排除项 {search_answer}')
                    toadd = Bank(catagory='挑战题', content=self.content, options=self.options, answer='', note=search_answer)
                    db.add(toadd)
                else:
                    log.debug(f'更新一题: 含排除项 {search_answer}')
                    bank.note += search_answer
                    db.update(bank)
                self.back()
                break
            except:
                log.debug(f'回答正确')
                num -= 1
                if not bank:
                    log.debug(f'新增一题: 含正确项 {search_answer}')
                    toadd = Bank(catagory='挑战题', content=self.content, options=self.options, answer=search_answer, note='')
                    db.add(toadd)
            time.sleep(delay)
        else: # end while
            log.info(f'已达成目标题数，等待30秒死亡 ...')
            time.sleep(30)
            self.back()
        return num

    def cycle(self):
        ''' 0. 在听广播时答题，可以节省视听学习时间
            1. 先做答题项目，因为新闻阅读过程不可避免遇到一篇视频将中断广播
            2. 最后根据积分情况进行灵活的视听学习
        '''
        view_time_obtain, view_time_total = self.bonus['视听学习时长']
        if view_time_obtain < view_time_total:
            self.bg_fm()
        else:
            log.info('视听学习时长已达标，跳过打开 FM')

        self.quiz()
        '''收藏、分享、评论 只要需要阅读就直接来一套，不阅读即忽略
            不要问为什么，因为作者就这么懒.-_-.
        '''
        read_obtain, read_total = self.bonus['阅读文章']
        read_time_obtain, read_time_total = self.bonus['文章学习时长']        
        if read_obtain == read_total and read_time_obtain == read_time_total:
            log.info(f'阅读文章篇数和时长均已完成，跳过学习')
        else:
            read_seconds = 120 * (read_time_total - read_time_obtain) 
            num = cfg.getint('prefer', 'count_read_ex')
            read_count = num + read_total - read_obtain
            delay = max(round(read_seconds / read_count), 10)
            ssc = cfg.getint('prefer', 'count_star_share_comment')
            self.read(read_count, delay, ssc)
        
        self.bonus = self._get_bonus()
        view_obtain, view_total = self.bonus['视听学习']
        view_time_obtain, view_time_total = self.bonus['视听学习时长']
        view_seconds = 180 * (view_time_total - view_time_obtain) # 单位：秒
        view_count = view_total - view_obtain
        if 0 == view_seconds and 0 == view_count:
            log.info(f'视听学习篇目和时长均已完成，跳过学习')
        elif 0 == view_seconds and 0 < view_count:
            delay_of_each_video = 10
            log.info(f'视听学习时长已完成，篇目未完成，以每则视频 {delay_of_each_video} 秒钟时间刷百灵')
            self.view_videos(view_count, delay_of_each_video)
        elif 0 < view_seconds and 0 == view_count:
            log.info(f'视听学习时长未完成，篇目已完成，打开新闻联播看 {view_seconds} 秒')
            self.view_newscast(view_seconds)
        else:
            log.info(f'视听学习篇目和时长均未完成，照着配置来咯')
            num = cfg.getint('prefer', 'count_view_ex')
            count = view_count + num
            delay = view_seconds // count + 5
            self.view_videos(count, delay)