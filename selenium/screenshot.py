from selenium import webdriver
from time import sleep
driver = webdriver.Firefox()
driver.get("https://www.youtube.com")


# scroll some more
for isec in (4, 3, 2, 1):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / %s);" % isec)
    sleep(1)

# load more
sleep(2)
print("push Load more...")
driver.find_element_by_css_selector('button.load-more-button').click()

print("wait a bit...")
sleep(2)

print("Jump to the bottom, work our way back up")
for isec in (1, 2, 3, 4, 5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / %s);" % isec)
    sleep(1)

driver.execute_script("window.scrollTo(0, 0)")
print("Pausin a bit...")
sleep(2)
print("Scrollin to the top so that the nav bar isn't funny looking")
driver.execute_script("window.scrollTo(0, 0);")


sleep(1)
print("Screenshotting...")
# screenshot
driver.save_screenshot("/tmp/youtube.com.jpg")
