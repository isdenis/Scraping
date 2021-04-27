from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/89.0.4389.128 Safari/537.36'}

main_link = 'https://lenta.ru/'
response = requests.get(main_link)
dom = html.fromstring(response.text)

news = dom.xpath("//section[contains(@class, 'b-top7-for-main')]//div[@class = 'item']")

news_db = []
for item in news:
    main_news = {}
    source_name = 'lenta.ru'
    news_name = item.xpath(".//a/text()")[0].replace('\xa0', ' ')
    news_link = f'{main_link}{item.xpath(".//a/@href")[0]}'
    date_publish = dom.xpath(".//a/time/@title")[0].replace(' апреля ', '.04.')
    main_news['source_name'] = source_name
    main_news['news_name'] = news_name
    main_news['link'] = news_link
    main_news['date_publish'] = date_publish
    news_db.append(main_news)

# Запись в БД
client = MongoClient('127.0.0.1', 27017)
db = client['news']
lenta_db = db.lenta_ru


# функция, которая записывает только новые вакансии в БД (если БД нет, то заливает все, что найдено).
def db_record(vac):
    if ('lenta_ru' in db.list_collection_names()) is False:
        lenta_db.insert_many(vac)
        print("Данные записаны в БД")
    else:
        for n in vac:
            search_result = lenta_db.find_one({
                'news_name': n['news_name'],
                'link': n['link'],
                'date_publish': n['date_publish']})
            if search_result is None:
                lenta_db.insert_one(n)
                pprint(f'Добавлена новая вакансия {n}')


db_record(news_db)




