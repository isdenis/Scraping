# текст письма полный

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint
from pymongo import MongoClient
import time


driver = webdriver.Chrome()

main_link = 'https://mail.ru/'
driver.get(main_link)

login = driver.find_element_by_xpath("//div/input[@name = 'login']")
login.send_keys('d_e_s_h_a@mail.ru') # study.ai_172@mail.ru
login.send_keys(Keys.ENTER)
time.sleep(1)
password = driver.find_element_by_xpath("//div/input[@name = 'password']")
password.send_keys('ufkz1989') #o%IyneXIrI11
password.send_keys(Keys.ENTER)

time.sleep(3)

# берем общее количество писем. Здесь иногда выходит кол-во писем, иногда идет просто "Входящие" и все.
mail_count = driver.find_element_by_xpath("//a[@href = '/inbox/']")
#m2 = mail_count.get_attribute('title').split(',')
m2 = 10


def get_link():
    get_links = set()
    actions = ActionChains(driver)
    while len(get_links) < m2:
        try:
            time.sleep(3)
            letters = driver.find_elements_by_xpath("//a[contains(@class, 'js-letter-list-item')]")
            letters[-1].send_keys(Keys.END)
            actions.perform()
            letters = driver.find_elements_by_xpath("//a[contains(@class, 'js-letter-list-item')]")
            for i in letters:
                #if i is not None:
                get_links.add(i.get_attribute('href'))
                print(len(get_links))
                #else:
                   # continue
        except:
            break
    return get_links


links = get_link()

mess_text = ''
mails_db = []
for mail_link in links:
    if mail_link is not None:
        mails = {}
        driver.get(mail_link)
        time.sleep(2)
        mails['from_who'] = driver.find_element_by_xpath("//div[@class = 'letter__author']/span").text
        mails['date'] = driver.find_element_by_class_name('letter__date').text  # дата
        mails['subject'] = driver.find_element_by_class_name('thread__subject').text  # тема письма
        mail_text = driver.find_elements_by_class_name('letter-body') # текст письма
        for mail_text in mail_text:
            mails['mail_text'] = mail_text.text
        mails_db.append(mails)
    else:
        continue

pprint(mails_db)

# Запись в БД
client = MongoClient('127.0.0.1', 27017)
db = client['mails']
mail_db = db.mails


def db_record(vac):
    if ('mails' in db.list_collection_names()) is False:
        mail_db.insert_many(vac)
        print("Данные записаны в БД")
    else:
        for n in vac:
            search_result = mail_db.find_one({
                'from_who': n['from_who'],
                'date': n['date'],
                'subject': n['subject']})
            if search_result is None:
                mail_db.insert_one(n)
                pprint(f'Добавлено новое письмо: {n}')


db_record(mails_db)
