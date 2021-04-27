from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient
from datetime import date

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/89.0.4389.128 Safari/537.36'}

link = 'https://yandex.ru/news/'
response = requests.get(link)
dom = html.fromstring(response.text)

news = dom.xpath("//div[contains(@class, 'news-top-flexible-stories')]//article")

news_db = []
for item in news:
    main_news = {}
    source_name = item.xpath(".//a[@class = 'mg-card__source-link']/@aria-label")[0].split(': ')[1]
    news_name = item.xpath(".//h2[@class = 'mg-card__title']/text()")[0].replace('\xa0', ' ')
    news_link = item.xpath(".//a[@class = 'mg-card__link']/@href")
    time_publish = item.xpath(".//span[@class = 'mg-card-source__time']/text()")
    main_news['source_name'] = source_name
    main_news['news_name'] = news_name
    main_news['link'] = news_link[0]
    main_news['date_publish'] = f'{date.today()}'.replace('-', '.')
    main_news['time_publish'] = time_publish[0]
    news_db.append(main_news)

# Запись в БД
client = MongoClient('127.0.0.1', 27017)
db = client['news']
yandex_db = db.yandex_news


# функция, которая записывает только новые вакансии в БД (если БД нет, то заливает все, что найдено).
def db_record(vac):
    if ('yandex_news' in db.list_collection_names()) is False:
        yandex_db.insert_many(vac)
        print("Данные записаны в БД")
    else:
        for n in vac:
            search_result = yandex_db.find_one({
                'news_name': n['news_name'],
                'link': n['link'],
                'date_publish': n['date_publish']})
            if search_result is None:
                yandex_db.insert_one(n)
                pprint(f'Добавлена новая вакансия {n}')


db_record(news_db)
