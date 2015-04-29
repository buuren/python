# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import time
from selenium.webdriver.common.keys import Keys


class Exasd(unittest.TestCase):
    def setUp(self):
        self.fp = webdriver.FirefoxProfile('C:/Users/username/AppData/Roaming/Mozilla/Firefox/Profiles/e4hcyoyy.default')
        #browser = webdriver.Firefox(fp)
        self.driver = webdriver.Firefox(self.fp)
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.molten-wow.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.mouse = webdriver.ActionChains(self.driver)
    
    def test_exasd(self):
        driver = self.driver
        driver.get(self.base_url)

        try:
            driver.find_element_by_id("userID")
            driver.find_element_by_id("userID").clear()
            driver.find_element_by_id("userID").send_keys("123")
            driver.find_element_by_id("userPW").clear()
            driver.find_element_by_id("userPW").send_keys("123")
            driver.find_element_by_id("userPW").send_keys(Keys.ENTER)
        except NoSuchElementException:
            print "User is already logged in"

        try:
            driver.find_element_by_xpath('//*[@id="rightBlock"]/div[2]/table/tbody/tr[4]/td[2]/a').click()
        except NoSuchElementException:
            print "Unable to find VOTE button. Using direct link..."
            driver.get('https://www.molten-wow.com/account/#0:0:0:1:0')

        try:
            driver.find_element_by_xpath('//*[@id="vform1"]/div').click()
        except NoSuchElementException:
            print 'Unable to vote for first voting site. Already voted?'
        else:
            driver.get("http://www.openwow.com/")
            driver.get("http://www.openwow.com/visit=6")

        try:
            driver.find_element_by_xpath('//*[@id="rightBlock"]/div[2]/table/tbody/tr[4]/td[2]/a').click()
        except NoSuchElementException:
            print "Unable to find VOTE button. Using direct link..."
            driver.get('https://www.molten-wow.com/account/#0:0:0:1:0')

        try:
            driver.find_element_by_xpath('//*[@id="vform2"]/div').click()
        except NoSuchElementException:
            print 'Unable to vote for second voting site. Already voted?'
        else:
            driver.get("http://www.xtremetop100.com/")
            driver.get("http://www.xtremetop100.com/out.php?site=1132296123")

    
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
