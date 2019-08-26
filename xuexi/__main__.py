import re
import json
import requests
import string
from time import sleep
from pathlib import Path
from urllib.parse import quote
from subprocess import check_call
from random import uniform, randint
from appium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .model import db, Bank
from .mconfig import cfg, rules
from .mloggger import logger as log


    

class Automation():
    # 初始化 appium_server 基本参数
    def __init__(self, wait_seconds):
        log.debug(f'打开 appium_server 服务器...')
        log.debug(f'配置 appium_server ...')
        self.driver = webdriver.Remote(self.driver_server, self.desired_caps)
        self.wait = WebDriverWait(self.driver, wait_seconds, 1)
        self.size = self.driver.get_window_size()

    def __del__(self):
        self.driver.close_app()

    def connect_device(self):
        pass

    def disconnect_device(self):
        pass

    # 屏幕方法
    def swipeUp(self):
        # 向上滑动屏幕
        self.driver.swipe(self.size['width'] * uniform(0.55, 0.65),
                          self.size['height'] * uniform(0.65, 0.75),
                          self.size['width'] * uniform(0.55, 0.65),
                          self.size['height'] * uniform(0.25, 0.35), uniform(800, 1200))
        log.debug(f'向上滑动屏幕')

    def swipeDown(self):
        # 向下滑动屏幕
        self.driver.swipe(self.size['width'] * uniform(0.55, 0.65),
                          self.size['height'] * uniform(0.25, 0.35),
                          self.size['width'] * uniform(0.55, 0.65),
                          self.size['height'] * uniform(0.65, 0.75), uniform(800, 1200))
        log.debug(f'向下滑动屏幕')

    def swipeRight(self):
        # 向右滑动屏幕
        self.driver.swipe(self.size['width'] * uniform(0.01, 0.11),
                          self.size['height'] * uniform(0.75, 0.89),
                          self.size['width'] * uniform(0.89, 0.98),
                          self.size['height'] * uniform(0.75, 0.89), uniform(800, 1200))
        log.debug(f'向右滑动屏幕')

    def click(self, rule):
        ele = self.wait.until(EC.presence_of_element_located((By.XPATH, rule)))
        log.debug(f'click {rule}')
        ele.click()
        sleep(1)

    def back(self):
        # https://blog.csdn.net/weixin_42082222/article/details/81298219
        self.driver.keyevent(4)
        log.debug(f'触发返回事件 ...')


class Xuexi(Automation):
    def __init__(self):
        self.driver_server = cfg.get('appium_server', 'driver_server')
        self.desired_caps = {
            "platformName": cfg.get('appium_server', 'platform_name'),
            "platformVersion": cfg.get('appium_server', 'platform_version'),
            "deviceName": cfg.get('appium_server', 'device_name'),
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

        # 初始化一个空白题
        self.catagory = ''
        self.content = ''
        self.options = []
        self.json_bank = self._load()

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

    def read_articles(self, num:int, delay:int):
        log.debug(f'阅读文章 {num} 篇 {delay} 秒/篇')

    def view_videos(self, num:int, delay:int):
        log.debug(f'视听学习 {num} 则 {delay} 秒/则')

    def get_score(self):
        log.debug(f'获取积分情况，根据积分情况执行相关动作')
        self.click(rules['mine'])
        self.click(rules['score_entry'])
        titles = '登录 阅读文章 视听学习 文章学习时长 视听学习时长 每日答题 每周答题 专项答题 挑战答题 订阅 收藏 分享 发表观点'.split(' ')
        scores = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['score_nums'])))
        for title, score in zip(titles, scores):
            res = score.get_attribute('name')
            obtain, total = [int(x) for x in re.findall(r'\d+', res)]
            log.debug(f'{title} {obtain} / {total} {obtain < total}')
        self.back()

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
        sleep(2)
        # step 2
        self.click(rules['quiz_entry'])

    def _get_note(self, count_edits=1)->bool:
        sleep(1)
        try:
            correct = self.driver.find_element_by_xpath(rules['correct'])
            log.debug(f'sorry, you did not choose the right answer')
        except:
            log.debug(f'NoSuchElment, which means you passed last question')
            return True
        if correct:
            answer = re.sub(r'正确答案：', '', correct.get_attribute('name'))
            note = self.driver.find_element_by_xpath(rules['note']).get_attribute('name') or ''
            bank = Bank(catagory=self.catagory, content=self.content, options=self.options, answer=answer, note=note)
            if count_edits > 1:
                log.debug(f'append bank to json')
                bank.options = count_edits
                self.json_bank.append(bank.to_dict())
            else:
                if '填空题' == self.catagory:
                    bank.options = 1
                log.debug(f'append bank to sqlite')
                log.debug(f'Bank {str(bank)}')
                db.add(bank)
            return False


    def _solve_blank(self):
        log.debug(f'这是一道填空题 ...')
        self.options = []
        texts = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['content_blank'])))
        # log.debug(texts)
        self.content = "".join([t.get_attribute('name').replace(u'\xa0', u' ') for t in texts])
        log.info(f'[填空题] {self.content}')        
        edits = self.driver.find_elements_by_xpath(rules['edit_text'])
        if not self.content:
            raise RuntimeError(f'没有捕获到填空题题干 ...')
        bank = db.query(content=self.content, catagory='填空题')
        if bank is not None:
            log.info(f'自动提交答案 {bank.answer}')
            answers = bank.answer.split(' ')
            for edit, answer in zip(edits, answers):
                edit.click()
                edit.send_keys(answer)
            else:
                self.click(rules['submit'])
        else:
            log.info(f'默认提交答案 不忘初心牢记使命')
            for edit in edits:
                edit.click()
                edit.send_keys('不忘初心牢记使命')
            else:
                self.click(rules['submit'])
        if not self._get_note(len(edits)):
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
        bank = db.query(content=self.content, catagory='单选题')
        if bank is not None:
            cursor = ord(bank.answer) - 65
            log.info(f'自动提交答案 {bank.answer}')
            options[cursor].click()
            self.click(rules['submit'])
        else: # 选最后一个
            log.info(f'默认提交答案 {chr(len(options)+64)}')
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
        bank = db.query(content=self.content, catagory='多选题')
        if bank is not None:
            log.info(f'自动提交答案 {bank.answer}')
            for option, answer in zip(options, ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']):
                if answer in bank.answer:
                    option.click()
            else:
                self.click(rules['submit'])
        else: # 全选
            log.info(f'默认提交答案 全选')
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

    def quiz_daily(self, forever=False):
        ''' 0. click 每日答题
            1. cycle 填空题、单选题、多选题
            2. score_reached? back: again
        '''
        log.debug(f'每日答题( {forever} )')
        log.debug(self.driver.contexts)
        delay = cfg.getint('prefer', 'delay_daily')
        # step 0
        self.click(rules['daily'])
        while True:
            for i in range(5):
                self._dispatch()
                sleep(2)
            try:
                reached = self.driver.find_element_by_xpath(rules['score_reached'])
                if not forever:
                    log.info(f'已达成今日份每日答题，返回')
                    self.click(rules['return'])
                    break
                else:
                    log.info(f'未达到6分, {delay} 秒后再来一组')
                    sleep(delay)
                    self.click(rules['next'])
                    continue 
            except:
                log.info(f'未达到6分, {delay} 秒后再来一组')
                sleep(delay)
                self.click(rules['next'])
                continue


    def quiz_weekly(self, auto=False):
        ''' 0. click 每周答题
        '''
        log.debug(f'每周答题')

    def quiz_monthly(self, auto=False):
        ''' 0. click 专项答题
        '''
        log.debug(f'专项答题')

    def _search(self, bank)->str:
        log.debug(f'正在问度娘')
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
            num -= 1
            log.debug(f'挑战答题 第 {num} 题')
            self.content = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['content_challenge']))).get_attribute('name').replace(u'\xa0', u' ')
            log.info(f'[挑战题] {self.content}')
            if not self.content:
                raise RuntimeError(f'没有捕获到挑战题 题干 ...')
            options = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['options_challenge'])))
            self.options = [o.get_attribute('name').replace('|', ' ') for o in options]
            log.debug(f'[选项] {self.options}')
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
            sleep(3)
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
                if not bank:
                    log.debug(f'新增一题: 含正确项 {search_answer}')
                    toadd = Bank(catagory='挑战题', content=self.content, options=self.options, answer=search_answer, note='')
                    db.add(toadd)
            sleep(delay)
        else: # end while
            log.info(f'已达成目标题数，等待30秒死亡 ...')
            sleep(30)
            self.back()
        return num

if __name__ == "__main__":
    app = Xuexi()
    app.get_score()
    app.quiz()    
    # app.quiz_daily()
    # app.quiz_challenge(900)
