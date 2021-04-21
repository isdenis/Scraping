from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from pprint import pprint

vacancys_hh = []
page = 0
page_count = 1
while int(page) < int(page_count):

    params = {'text': 'python',
              'area': '76', # 76 - Ростов-на-Дону, 1 - Москва
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

# запишем все вакансии со страницы в переменную vacancy
    vacancy_all = dom.find_all('div', {'class': 'vacancy-serp-item'})

# разбор одной вакансии
    for vacancy in vacancy_all:
        current_vacancy = {}

        # получение названия
        vacancy_name_hh = vacancy.find('a', {'class': 'bloko-link'}).getText()

        # получение предлагаемой зарплаты (минимальная, максимальная и валюта)
        compensation_min_hh = ''
        compensation_max_hh = ''
        compensation_currency_hh = ''
        try:
            vacancy_compensation = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()\
                                    .replace('\u202f', '').split(' ')
            for i in vacancy_compensation:
                if i is None:
                    continue
                elif i.lower() == 'от':
                    vacancy_compensation[0] = vacancy_compensation[1]
                    vacancy_compensation[1] = None
                elif i.lower() == 'до':
                    vacancy_compensation[0] = None
                elif i.lower() in ('руб.', 'eur', 'usd'):
                    vacancy_compensation[2] = i
                elif i.isdigit() is False:
                    vacancy_compensation.remove(i)
            compensation_min_hh = vacancy_compensation[0]
            compensation_max_hh = vacancy_compensation[1]
            compensation_currency_hh = vacancy_compensation[2]
        except:
            compensation_min_hh = None
            compensation_max_hh = None
            compensation_currency_hh = None

# получение ссылки на саму вакансию
        vacancy_href_hh = vacancy.find(('a', {'class': 'bloko-link'})).get('href')

# записываем данные в переменную current_vacancy
        current_vacancy['name'] = vacancy_name_hh
        current_vacancy['compensation_min'] = compensation_min_hh
        current_vacancy['compensation_max'] = compensation_max_hh
        current_vacancy['compensation_currency'] = compensation_currency_hh
        current_vacancy['link'] = vacancy_href_hh
        current_vacancy['web'] = 'hh.ru'
        vacancys_hh.append(current_vacancy)

    page += 1

vac_all = pd.DataFrame(vacancys_hh)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

pprint(vac_all)