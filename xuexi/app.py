from appium import webdriver
from .config import cfg
from .logger import log

class Automation():
    # 初始化 Appium 基本参数
    def __init__(self, APP_PACKAGE, APP_ACTIVITY):
        self.desired_caps = {
            "platformName": cfg.get('APPIUM', 'PLAT_FORM_NAME'),
            "platformVersion": cfg.get('APPIUM', 'PLAT_FORM_VERSION'),
            "deviceName": cfg.get('APPIUM', 'DEVICE_NAME'),
            "appPackage": cfg.get('APPIUM', 'APP_PACKAGE'),
            "appActivity": cfg.get('APPIUM', 'APP_ACTIVITY'),
            "unicodeKeyboard": cfg.get('APPIUM', 'UNICODE_KEYBOARD'),
            "resetKeyboard": cfg.get('APPIUM', 'RESET_KEYBOARD'),
            "noReset": cfg.get('APPIUM', 'NO_RESET')
        }
        print('打开 appium 服务器...')
        print('配置 appium ...')
        self.driver = webdriver.Remote(DRIVER_SERVER, self.desired_caps)
        self.wait = WebDriverWait(self.driver, 10)
        self.size = self.driver.get_window_size()