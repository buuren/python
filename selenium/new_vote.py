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
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.molten-wow.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.mouse = webdriver.ActionChains(self.driver)
    
    def test_exasd(self):
        driver = self.driver
        driver.get(self.base_url)

        command_list = [
            'driver.find_element_by_id("userID").clear()',
            'driver.find_element_by_id("userID").send_keys("user")',
            'driver.find_element_by_id("userPW").clear()',
            'driver.find_element_by_id("userPW").send_keys("pass")',
            'driver.find_element_by_id("userPW").send_keys(Keys.ENTER)',
            'driver.get("https://www.molten-wow.com/account/#5:1:0:0:0")',
            'driver.get("http://www.openwow.com/vote=6")',
            'driver.get("http://www.openwow.com/")',
            'driver.get("http://www.openwow.com/visit=6")',
            'driver.get("https://www.molten-wow.com/account/#5:1:0:0:0")',
            'driver.get("http://www.xtremetop100.com/in.php?site=1132296123")',
            'driver.get("http://www.xtremetop100.com/")',
            'driver.get("http://www.xtremetop100.com/out.php?site=1132296123")'
        ]

        for eachCommand in command_list:
            exec eachCommand
            time.sleep(3)


        time.sleep(5)
    
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
