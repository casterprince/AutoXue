import re
from time import sleep
from subprocess import check_call
from random import uniform, randint
from appium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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
        sleep(5)

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
        log.debug(f'click {ele}')
        ele.click()

    def back(self):
        # https://blog.csdn.net/weixin_42082222/article/details/81298219
        self.driver.keyevent(4)
        log.debug(f'KEYCODE_BACK pressed')


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
            "noReset": cfg.get('appium_server', 'no_reset')
        }
        wait_seconds = cfg.getint('appium_server', 'wait_seconds')
        super().__init__(wait_seconds)



    def read_articles(self, num:int, delay:int):
        log.debug(f'阅读文章 {num} 篇 {delay} 秒/篇')

    def view_videos(self, num:int, delay:int):
        log.debug(f'视听学习 {num} 则 {delay} 秒/则')

    def quiz(self):
        ''' 0. click 學習（刷新）
            1. click 我的
            2. click 我要答题
            3. Callback: quiz_daily, quiz_weekly, quiz_monthly, quiz_challenge
            4. keyevent KEYCODE_BACK
        '''
        log.debug(f'我要答题')
        
        # step 0
        self.wait.until(EC.presence_of_element_located((By.XPATH, rules['work']))).click()
        # step 1
        self.wait.until(EC.presence_of_element_located((By.XPATH, rules['mine']))).click()
        # step 2
        self.wait.until(EC.presence_of_element_located((By.XPATH, rules['quiz']))).click()

    def _solve_blank(self):
        log.debug(f'这是一道填空题 ...')
        contents = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['content_blank'])))
        text = "".join([content.get_attribute('name').replace(u'\xa0', u' ') for content in contents])
        log.debug(f'[填空题] {text}')
        edits = self.driver.find_elements_by_xpath(rules['edit_text'])
        for edit in edits:
            edit.click()
            edit.send_keys('不忘初心牢记使命')
        self.click(rules['submit'])


    def _solve_radio(self):
        log.debug(f'这是一道单选题 ...')
        content = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['content_radio_check']))).get_attribute('name').replace(u'\xa0', u' ')
        log.debug(f'[单选题] {content}')
        options = self.driver.find_elements_by_xpath(rules['options_radio_check'])
        options_content = [option.get_attribute('name').replace('|', ' ') for option in options]
        log.debug(f'[选项] {options_content}')
        options[-1].click()
        self.click(rules['submit'])

    def _solve_check(self):
        log.debug(f'这是一道多选题 ...')
        content = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['content_radio_check']))).get_attribute('name').replace(u'\xa0', u' ')
        log.debug(f'[多选题] {content}')
        options = self.driver.find_elements_by_xpath(rules['options_radio_check'])
        options_content = [option.get_attribute('name').replace('|', ' ') for option in options]
        log.debug(f'[选项] {options_content}')
        for option in options:
            option.click()
        self.click(rules['submit'])

    def _dispatch(self):
        ''' 0. get category
            1. switch to sub func
            2. exit or again
        '''
        log.debug(f'开始分派 ...')
        category = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['category']))).get_attribute('name')
        # self.driver.find_element_by_xpath(rules['category']).get
        print(category)
        if '填空题' == category:
            self._solve_blank()
        elif '单选题' == category:
            self._solve_radio()
        elif '多选题' == category:
            self._solve_check()
        else:
            log.debug(f'未知的题目类型 {category}')

    def quiz_daily(self, auto=True, forever=False):
        ''' 0. click 每日答题
            1. cycle 填空题、单选题、多选题
            2. score_reached? back: again
        '''
        log.debug(f'每日答题( {forever} )')
        print(self.driver.contexts)
        # step 0
        self.click(rules['daily'])
        self._dispatch()


    def quiz_weekly(self, auto=False):
        ''' 0. click 每周答题
        '''
        log.debug(f'每周答题')

    def quiz_monthly(self, auto=False):
        ''' 0. click 专项答题
        '''
        log.debug(f'专项答题')

    def quiz_challenge(self, num:int, dealy:int):
        ''' 0. click 挑战答题
            1. cycle 挑战题
            2. question_count_reached? back: again
        '''
        if delay <= 0 or delay > 5:
            delay = randint(1, 5)
        log.debug(f'挑战答题 {num} 题 延时提交 {delay} 秒/题')

if __name__ == "__main__":
    app = Xuexi()
    app.quiz()
    app.quiz_daily()
