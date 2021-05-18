from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/89.0.4389.128 Safari/537.36'}


# собираем все новости
def news_count(link):
    news_db = []
    for n in link:
        main_news = {}
        response_2 = requests.get(n)
        dom_2 = html.fromstring(response_2.text)
        source_name = dom_2.xpath("//span[@class = 'breadcrumbs__item']//a//text()")
        news_name = dom_2.xpath("//span[@class = 'hdr__text']//h1//text()")
        news_link = n
        when_publish = dom_2.xpath(
            "//span[@class = 'breadcrumbs__item']//span[contains(@class,'breadcrumbs__text ')]/@datetime")
        date_publish = when_publish[0].split('T')[0].replace('-', '.')
        time_publish = when_publish[0].split('T')[1].split('+')[0]
        main_news['source_name'] = source_name[0]
        main_news['news_name'] = news_name[0]
        main_news['link'] = news_link
        main_news['date_publish'] = date_publish
        main_news['time_publish'] = time_publish
        news_db.append(main_news)
    return news_db


# соберем все ссылки
main_link = 'https://news.mail.ru/'
response = requests.get(main_link)
dom = html.fromstring(response.text)

links = []
news = dom.xpath("//li")
print(len(news))
for item in news:
    link = item.xpath(".//a/@href")
    text = item.xpath(".//a//text()")
    links.append(link[0])

all_news = news_count(links)

# Запись в БД
client = MongoClient('127.0.0.1', 27017)
db = client['news']
mail_db = db.mail_ru


# функция, которая записывает только новые вакансии в БД (если БД нет, то заливает все, что найдено).
def db_record(vac):
    if ('mail_ru' in db.list_collection_names()) is False:
        mail_db.insert_many(vac)
        print("Данные записаны в БД")
    else:
        for n in vac:
            search_result = mail_db.find_one({
                'news_name': n['news_name'],
                'link': n['link'],
                'date_publish': n['date_publish']})
            if search_result is None:
                mail_db.insert_one(n)
                pprint(f'Добавлена новая новость: {n}')


db_record(all_news)
