#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/13 11:08
# @Author  : sgwang
# @File    : taobao_login.py
# @Software: PyCharm
import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

TB_LOGIN_URL = 'https://login.taobao.com/member/login.jhtml'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"


class Login:

    def __init__(self, account, password):
        self.browser = None
        self.account = account
        self.password = password

    def open(self, url):
        self.browser.get(url)
        self.browser.implicitly_wait(20)

    def switch_to_password_mode(self):
        """
        切换到密码模式
        :return:
        """
        if self.browser.find_element_by_id('J_QRCodeLogin').is_displayed():
            self.browser.find_element_by_id('J_Quick2Static').click()

    def write_username(self, username):
        """
        输入账号
        :param username:
        :return:
        """
        try:
            username_input_element = self.browser.find_element_by_id('fm-login-id')
        except:
            username_input_element = self.browser.find_element_by_id('TPL_username_1')

        username_input_element.clear()
        username_input_element.send_keys(username)

    def write_password(self, password):
        """
        输入密码
        :param password:
        :return:
        """

        try:
            password_input_element = self.browser.find_element_by_id("fm-login-password")
        except:
            password_input_element = self.browser.find_element_by_id('TPL_password_1')

        password_input_element.clear()
        password_input_element.send_keys(password)

    def lock_exist(self):
        """
        判断是否存在滑动验证
        :return:
        """
        if self.is_element_exist('#baxia-dialog-content'):
            # 如果存在iframe，切换到iframe
            iframe = self.browser.find_element_by_id("baxia-dialog-content")
            self.browser.switch_to_frame(iframe)

        return self.is_element_exist('#nc_1_wrapper') and self.browser.find_element_by_id('nc_1_wrapper').is_displayed()

    def unlock(self, times=10):
        """
        执行滑动解锁
        :return:
        """
        if self.is_element_exist("#nocaptcha > div > span > a"):
            self.browser.find_element_by_css_selector("#nocaptcha > div > span > a").click()

        bar_element = self.browser.find_element_by_id('nc_1_n1z')
        ActionChains(self.browser).drag_and_drop_by_offset(bar_element, 258, 0).perform()
        if self.is_element_exist("#nocaptcha > div > span > a"):
            times -= 1
            if times <= 0:
                return
            self.unlock(times)
        time.sleep(0.5)

        # 返回到主页面
        self.browser.switch_to_default_content()

    def login_lock_exist(self):
        """
        判断是否存在滑动验证
        :return:
        """
        if self.is_element_exist('#baxia-dialog-content'):
            # 如果存在iframe，切换到iframe
            iframe = self.browser.find_element_by_id("baxia-dialog-content")
            self.browser.switch_to_frame(iframe)

        return self.is_element_exist('#nc_1_n1z') and self.browser.find_element_by_id('nc_1_n1z').is_displayed()

    def login_unlock(self, times=10):
        """
        执行滑动解锁
        :return:
        """
        if self.is_element_exist("#nc_1_n1z"):
            self.browser.find_element_by_css_selector("#nc_1_n1z").click()

        bar_element = self.browser.find_element_by_id('nc_1_n1z')
        ActionChains(self.browser).drag_and_drop_by_offset(bar_element, 258, 0).perform()
        if self.is_element_exist("#nc_1_n1z"):
            times -= 1
            if times <= 0:
                return
            self.unlock(times)
        time.sleep(0.5)

        # 返回到主页面
        self.browser.switch_to_default_content()

    def submit(self):
        """
        提交登录
        :return:
        """
        try:
            self.browser.find_element_by_css_selector("#login-form > div.fm-btn > button").click()
        except:
            self.browser.find_element_by_id('J_SubmitStatic').click()

        time.sleep(0.5)
        if self.is_element_exist("#J_Message"):
            self.write_password(self.password)
            self.submit()
            time.sleep(5)

    def is_element_exist(self, selector):
        """
        检查是否存在指定元素
        :param selector:
        :return:
        """
        try:
            self.browser.find_element_by_css_selector(selector)
            return True
        except NoSuchElementException:
            return False

    def init_browser(self):
        """
        初始化selenium浏览器
        :return:
        """
        headless, options = False, Options()

        try:
            # 取消沙盒模式，解决DevToolsActivePort文件不存在的报错
            options.add_argument('--no-sandbox')
            # 禁用通知警告
            options.add_argument('–disable-notifications')
            # 针对Linux环境下的chrome参数。大量渲染时，写入/tmp而非/dev/shm
            options.add_argument('--disable-dev-shm-usage')
            # 配置代理
            # options.add_argument('--proxy-server=http://ip:port')
            # 反爬虫识别，window.navigator.webdriver='undefined'。版本94 正式版
            options.add_argument('--disable-blink-features=AutomationControlled')

            # 不显示chrome正受到自动测试软件的控制。地址栏位置
            options.add_experimental_option("excludeSwitches", ['enable-automation'])

            # 1是加载图片，2是不加载图片
            prefs = {"profile.managed_default_content_settings.images": 1}
            options.add_experimental_option("prefs", prefs)

            # 设置user-agent
            options.add_argument(f'--user-agent={USER_AGENT}')

            if headless:
                # 无界面模式
                options.add_argument('--headless')
                # 禁用gpu渲染
                options.add_argument('--disable-gpu')

            # 加载驱动
            self.browser = webdriver.Chrome(executable_path="drivers" + os.sep + "chromedriver", options=options)

            # 隐式等待，是设置全局的查找页面元素的等待时间，在这个时间内没找到指定元素则抛出异常，只需设置一次
            self.browser.implicitly_wait(3)
            self.browser.maximize_window()
        except WebDriverException as ex:
            # 驱动问题
            print("ERROR", "浏览器错误", "请检查你下载并解压好的驱动是否放在drivers目录下")
            sys.exit(1)

    def start(self):
        try:
            # 1 初始化浏览器，打开淘宝登录页
            self.init_browser()
            self.browser.get(TB_LOGIN_URL)

            # 2 输入用户名，输入密码
            self.write_username(self.account)
            self.write_password(self.password)

            # 3 如果有滑块 移动滑块
            if self.lock_exist():
                self.unlock()

            # 4 点击登录按钮
            self.submit()

            # 5 再判断是否存在滑块
            if self.login_lock_exist():
                self.login_unlock()

            # 6 登录成功，直接请求页面
            print("登录成功，跳转至目标页面进行处理")

            # 这里可以写一些登录后需要python处理的逻辑
            # self.browser.get('https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm')
            print("over")
            time.sleep(1000)
        except:
            # 主动关闭浏览器
            if self.browser:
                self.browser.quit()


def get_environ(param, required=True) -> str:
    """
    :param: param 参数字符串
    :param: required 是否检验标记。默认必填
    :return: str
    """
    tb_param = os.environ.get(param, None)
    if required and tb_param is None:
        print(f"{param}不能为空！填写方式：github -> setting -> secret！")
        sys.exit()
    return tb_param


if __name__ == "__main__":
    # action中设置的值
    TB_account = get_environ("TB_account", required=True)
    TB_password = get_environ("TB_password", required=True)

    Login(TB_account, TB_password).start()
