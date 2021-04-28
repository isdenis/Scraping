# от кого,
# дата отправки,
# тема письма,
# текст письма полный

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time

driver = webdriver.Chrome()

main_link = 'https://mail.ru/'
driver.get(main_link)

login = driver.find_element_by_xpath("//div/input[@name = 'login']")
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.ENTER)
time.sleep(1)
password = driver.find_element_by_xpath("//div/input[@name = 'password']")
password.send_keys('o%IyneXIrI11')
password.send_keys(Keys.ENTER)

time.sleep(3)

get_links = []
def get_link():
    global get_links
    actions = ActionChains(driver)
    for n in range(5):
        mail = driver.find_elements_by_xpath("//a[contains(@class, 'js-letter-list-item')]")
        for i in mail:
            link = i.get_attribute('href')
            if link not in get_links:
                get_links.append(link)
            else:
                continue
        for m in range(25):
            actions.send_keys(Keys.DOWN)
            actions.perform()
    return get_links


links = get_link()
print(links)
