# -*- coding: utf-8 -*-

from selenium import webdriver
import unittest
import time
import sys


class Vote(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def vote_for_me(self):
        driver = self.driver
        driver.set_page_load_timeout(10)

        urls = []
        passed = False
        done = False

        vote1_url = "http://www.google.com"
        vote2_url = "http://www.gmail.com"
        vote3_url = "http://www.yahoo.com"
        vote4_url = "http://www.swedbank.ee"

        urls.extend((vote1_url, vote2_url, vote3_url, vote4_url))

        while not done:
            while not passed:
                results = []
                try:
                    for each_url in urls:
                        try:
                            print "-----------------------------------------------------"
                            print "Opening: ", each_url
                            driver.get(each_url)
                            print "Page loaded."
                            time.sleep(5)
                        except Exception:
                            print 'Another error: ', sys.exc_info()[0]
                            results.append(0)
                            time.sleep(5)
                            break
                        else:
                            results.append(1)
                finally:
                    if 0 in results:
                        print "There were failed checks."
                    else:
                        print "All pages loaded in less than 5 seconds. Starting to vote..."
                        passed = True

            time.sleep(60)
            driver.get(vote1_url)

            try:
                driver.find_element_by_id("strID").clear()
                driver.find_element_by_id("strID").send_keys("therazor")
                driver.find_element_by_id("strPW").clear()
                driver.find_element_by_id("strPW").send_keys("therazor")
                driver.find_element_by_css_selector("p").click()
                driver.find_element_by_css_selector("p").click()
                driver.find_element_by_xpath("//div[@id='rightBlock']/div[2]/table/tbody/tr[4]/td[2]/div/p").click()
            except Exception:
                print 'Failed to login to website.'
                continue

            time.sleep(2)
            driver.get(vote1_url + "/account/#0:1:0:0:0")
            time.sleep(5)

            try:
                driver.find_element_by_css_selector("#vform1 > div.cpBtn").click()
            except Exception:
                print "Could not find vote button. Exit"
                continue

            time.sleep(3)
            driver.get(vote2_url + "/visit=6")
            time.sleep(3)
            driver.find_element_by_css_selector("#vform2 > div.cpBtn > p").click()
            time.sleep(2)
            driver.get(vote3_url + "/out.php?site=1132296123")
            time.sleep(3)
            driver.find_element_by_css_selector("#vform3 > div.cpBtn > p").click()
            time.sleep(2)
            driver.get(vote4_url + "/out.asp?id=44178")
            time.sleep(5)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
