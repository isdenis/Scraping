from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pprint import pprint
from pymongo import MongoClient
import json
import time


driver = webdriver.Chrome()


main_link = 'https://www.mvideo.ru/'
driver.get(main_link)
time.sleep(2)

#берем количество элементов
count_elements = driver.find_element_by_xpath('//ul[contains(@data-init-param, "Новинки")]').get_attribute('data-init-param')
count_elements = json.loads(count_elements)
count_elements = count_elements['ajaxContentLoad']['total']
print(f'Должно быть товаров в списке: {count_elements}')

# переходим к блоку "новинки" для подгрузки
new = driver.find_element_by_xpath('//div[contains(text(), "Новинки")]')
actions = ActionChains(driver)
actions.move_to_element(new)
actions.send_keys(Keys.PAGE_DOWN)
actions.perform()

# считаем кол-во элементов сейчас
elements = driver.find_elements_by_xpath('//ul[contains(@data-init-param, "Новинки")]//li')

# подгружаем остальные элементы нажимая на кнопку "далее"
while len(elements) < count_elements:
    elements = driver.find_elements_by_xpath('//ul[contains(@data-init-param, "Новинки")]//li')
    next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//ul[contains\
                                            (@data-init-param, "Новинки")]/following::a[2]')))
    next_button.click()
else:
    print(len(elements))


# записываем хар-ки товаров
description = driver.find_elements_by_xpath('//ul[contains(@data-init-param, "Новинки")]\
                                            //li[@class="gallery-list-item"]\
                                            //a[@class="fl-product-tile-picture fl-product-tile-picture__link"]')
all_elem = []
for descr in description:
    try:
        descr = descr.get_attribute('data-product-info')
        descr = json.loads(descr)
        all_elem.append(descr)
    except:
        print('Один товар не будет записан')
        continue

print(f'Будет записано {len(all_elem)} товаров')

# Запись в БД
client = MongoClient('127.0.0.1', 27017)
db = client['mvideo']
mvideo_db = db.mvideo


def db_record(vac):
    if ('mvideo' in db.list_collection_names()) is False:
        mvideo_db.insert_many(vac)
        print("Данные записаны в БД")
    else:
        for n in vac:
            search_result = mvideo_db.find_one({
                'productName': n['productName'],
                'productVendorName': n['productVendorName'],
                'productPriceLocal': n['productPriceLocal']})
            if search_result is None:
                mvideo_db.insert_one(n)
                pprint(f'Добавлена новая новость: {n}')


db_record(all_elem)
