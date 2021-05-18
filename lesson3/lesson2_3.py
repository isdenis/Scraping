from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import re
from pprint import pprint

vacancys_hh = []
page = 0
page_count = 1
while int(page) < int(page_count):

    params = {'text': 'python',
              'area': '76',  # 76 - Ростов-на-Дону, 1 - Москва
              'page': page}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                                    Chrome/89.0.4389.114 Safari/537.36'}

    main_url = 'https://hh.ru/search/vacancy'
    response = requests.get(main_url, params=params, headers=headers)

    dom = bs(response.text, 'html.parser')

    # находим кол-во страниц
    vacancy_count = dom.find('span', {'class': 'bloko-button-group'})
    for i in vacancy_count.children:
        u = i.getText()
        if int(u) > int(page_count):
            page_count = u

    # запишем все вакансии со страницы в переменную vacancy_all
    vacancy_all = dom.find_all('div', {'class': 'vacancy-serp-item'})

    # разбор одной вакансии
    for vacancy in vacancy_all:
        current_vacancy = {}

        # получение названия
        vacancy_name_hh = vacancy.find('a', {'class': 'bloko-link'}).getText()

        # получение предлагаемой зарплаты (минимальная, максимальная и валюта) и запись данные в current_vacancy
        try:
            # Вчера работала замена пробела в ЗП, а сегодня нет. Посмотрел - поменяли \u202f на \xa0
            vacancy_compensation = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText() \
                .replace('\xa0', '') \
                .replace('\u202f', '') \
                .replace('-', ' ') \
                .split(' ')
            if vacancy_compensation[0].lower() == 'от':
                current_vacancy['compensation_min'] = int(vacancy_compensation[1])
                current_vacancy['compensation_max'] = None
            if vacancy_compensation[0].lower() == 'до':
                current_vacancy['compensation_max'] = int(vacancy_compensation[1])
                current_vacancy['compensation_min'] = None
            if vacancy_compensation[0].isdigit() is True and vacancy_compensation[1].isdigit() is True:
                current_vacancy['compensation_min'] = int(vacancy_compensation[0])
                current_vacancy['compensation_max'] = int(vacancy_compensation[1])
            if vacancy_compensation[2].lower() in ('руб.', 'eur', 'usd'):
                current_vacancy['compensation_currency'] = vacancy_compensation[2]
        except:
            current_vacancy['compensation_min'] = None
            current_vacancy['compensation_max'] = None
            current_vacancy['compensation_currency'] = None

        # получение ссылки на саму вакансию
        vacancy_href_hh = vacancy.find(('a', {'class': 'bloko-link'})).get('href')

        # записываем данные о наименовании вакансии и линк в переменную current_vacancy
        current_vacancy['name'] = vacancy_name_hh
        current_vacancy['link'] = vacancy_href_hh
        current_vacancy['web'] = 'hh.ru'
        vacancys_hh.append(current_vacancy)

    page += 1

vac_all = pd.DataFrame(vacancys_hh)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)


# запускаем mongo
client = MongoClient('127.0.0.1', 27017)
db = client['jobs']
vacancy_db = db.vacancy


# функция, которая записывает весь результат поиска в ДБ
def db_record(vac):
    vacancy_db.insert_many(vac)
    print("Данные записаны в БД")


db_record(vacancys_hh)


# функция, которая записывает только новые вакансии в БД (если БД нет, то заливает все, что найдено).
def db_record(vac):
    if ('vacancy' in db.list_collection_names()) is False:
        vacancy_db.insert_many(vac)
        print("Данные записаны в БД")
    else:
        for n in vac:
            search_result = vacancy_db.find_one({
                'compensation_min': n['compensation_min'],
                'compensation_max': n['compensation_max'],
                'link': n['link']})
            if search_result is None:
                vacancy_db.insert_one(n)
                pprint(f'Добавлена новая вакансия {n}')


db_record(vacancys_hh)


# функция, которая производит поиск и выводит на экран вакансии с ЗП
def find_job(summ):
    for job in vacancy_db.find({'$or': [{'compensation_min': {'$gt': summ}}, {'compensation_max': {'$gt': summ}}]}):
        pprint(job)


find_job(int(input('Какая зарплата интересует: ')))
