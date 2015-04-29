# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import unittest, time, re
import time


class SBCralwer(unittest.TestCase):
    def setUp(self):
        self.d = DesiredCapabilities.FIREFOX
        self.d['loggingPrefs'] = {'browser': 'ALL'}
        self.fp = webdriver.FirefoxProfile('C:/Users/123123/AppData/Roaming/Mozilla/Firefox/Profiles/e4hcyoyy.default')

        self.fp.set_preference("extensions.firebug.console.enableSites", True)
        self.fp.set_preference("extensions.firebug.net.enableSites", True)
        self.fp.set_preference("extensions.firebug.net.enableSites", True)
        self.fp.set_preference("extensions.firebug.allPagesActivation", "on")

        self.driver = webdriver.Firefox(self.fp, capabilities=self.d)
        self.driver.implicitly_wait(10)
        self.base_url = "https://www.hello.com"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.mouse = webdriver.ActionChains(self.driver)


    def test_SBCralwer(self):
        driver = self.driver

        urlList = [u'']

        for eachUrl in urlList:
            print 'openning link %s' % (self.base_url + '/' + eachUrl)

            driver.get(self.base_url + '/' + eachUrl)

            for entry in driver.get_log('browser'):
                if "Unknown property" in entry['message'] or "eclaration" in entry['message'] or "Expected media" in entry['message'] or "deprecated" in entry['message']:
                    pass
                else:
                    print entry['message']

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
