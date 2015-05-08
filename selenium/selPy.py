from selenium import webdriver
import multiprocessing
from multiprocessing import Manager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
import datetime
from random import randint


class SeleniumLib(multiprocessing.Process):

    instanceCounter = 0

    def __init__(self, rooturl, ffprofilepath, urlarray, screenshotdir=None):
        multiprocessing.Process.__init__(self)
        objectManager = Manager()
        self.urlDictionary = objectManager.dict()

        type(self).instanceCounter += 1

        self.urlarray = urlarray
        self.rooturl = rooturl
        self.ffprofilepath = ffprofilepath
        self.screenshotdir = screenshotdir

    #================= Firefox profiles ================================

    def create_capabilities_profile(self):
        """ Firefox webdriver with firebug console."""

        firefoxprofile = webdriver.FirefoxProfile(self.ffprofilepath)
        firefoxprofile.set_preference("extensions.firebug.console.enableSites", True)
        firefoxprofile.set_preference("extensions.firebug.net.enableSites", True)
        firefoxprofile.set_preference("extensions.firebug.net.enableSites", True)
        firefoxprofile.set_preference("extensions.firebug.allPagesActivation", "on")

        extracapabilites = DesiredCapabilities.FIREFOX
        extracapabilites['loggingPrefs'] = {'browser': 'ALL'}

        driverwithcapabilities = webdriver.Firefox(firefoxprofile, capabilities=extracapabilites)
        return driverwithcapabilities

    def create_default_profile(self):

        """ Basic webdriver profile"""

        firefoxprofile = webdriver.FirefoxProfile(self.ffprofilepath)
        driverdefault = webdriver.Firefox(firefoxprofile)
        return driverdefault

    # ======================== Start cases here ==================================

    def testcase_take_screenshot(self):

        """ Open URL and create a screenshot
            Requires argument: urlList - a list of coma separated URLs to open.
        """

        driver = self.create_default_profile()
        urldir = re.findall(r'https?://(.*)', self.rooturl)[0].replace('.', '')

        try:
            for eachUrl in self.urlarray:
                driver.get(self.rooturl + "/" + eachUrl)
                try:
                    driver.save_screenshot(self.screenshotdir + '/' + urldir + '/' + eachUrl.replace('/', '') + '.png')
                except:
                    print 'Cannot save screenshot %s' % (self.screenshotdir + '/' + urldir + '/' + eachUrl.replace('/', '') + '.png')
        except Exception as ex:
            print "[testCase_take_screenshot] Unable to open url: %s" % (self.rooturl + "/" + eachUrl)
            print ex
        finally:
            driver.close()

    def testcase_search_in_console(self):

        """Test case with capabilities to scan browser console log"""

        print 'Starting process: [%s]' % self.name
        driver = self.create_capabilities_profile()

        try:
            eachUrl = None
            for eachUrl in self.urlarray:
                urlopen = self.rooturl + "/" + eachUrl
                startloadtime = datetime.datetime.now()

                driver.get(urlopen)

                for entry in driver.get_log('browser'):
                    if 'mixed' in entry['message']:
                        print 'Mixed content: %s' % urlopen

                endloadtime = datetime.datetime.now() - startloadtime
                self.urlDictionary[urlopen] = endloadtime.total_seconds()

        except Exception as ex:
            print "[testCase_search_in_console] Unable to open url: %s" % eachUrl
            print ex

        driver.close()

    def testcase_search_in_htmlsoruce(self):
        driver = self.create_default_profile()

        try:
            for eachUrl in self.urlarray:
                driver.get(self.rooturl + "/" + eachUrl)

                for each_html_source_line in driver.page_source:
                    if '.swf' in each_html_source_line:
                        print self.rooturl + "/" + eachUrl

        except Exception as ex:
            print "[testCase_take_screenshot] Unable to open url: %s" % (self.rooturl + "/" + eachUrl)
            print ex
        finally:
            driver.close()


    def run(self):
        self.testcase_search_in_htmlsoruce()


if __name__ == '__main__':

    firefoxProcessCount = 4


    fromList = ['http://zzz.ee/']

    splitArray = []
    counter = 0

    for each_sub_array in range(firefoxProcessCount):
        splitArray.append([])

        remainder = 0
        if counter < len(urlList) % firefoxProcessCount:
            remainder = 1

        addToArray = (len(urlList)/firefoxProcessCount) + remainder

        for m_counter in range(addToArray):
            splitArray[len(splitArray) -1].append(urlList[counter])
            counter += 1

    jobs = [SeleniumLib(
            'https://www.zzz.ee',
            'C:/Users/p998sqb/AppData//Roaming/Mozilla/Firefox/Profiles/e4hcyoyy.default',
            eachArray,
            screenshotdir='C:/Users/p998sqb/Desktop/screns')
            for eachArray in splitArray
        ]

    for workJob in jobs:
        workJob.start()

    for workJob in jobs:
        workJob.join()

    for workJob in jobs:
        data_array = dict(workJob.urlDictionary)

        print "-----------------------------------------------------------------"
        print 'Finished jobs [%s] in %s seconds. Scanned: %s links.\nAverage load time: %s\nHighest load time: %s[%s]\nFastest: %s[%s]' % (
            workJob._name,
            sum([urltime for urltime in data_array.values()]),
            len(data_array),
            reduce(lambda urlname, urltime: urlname + urltime, data_array.values()) / len(data_array.values()),
            max(data_array.values()),
            [url for url, urlTime in data_array.iteritems() if urlTime == max(val for val in data_array.values())][0],
            min(data_array.values()),
            [url for url, urlTime in data_array.iteritems() if urlTime == min(val for val in data_array.values())][0]
        )

    print 'All jobs are done'

