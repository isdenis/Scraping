from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lm import settings
from lm.spiders.lmru import LmruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    query = input(f'Что нужно спарсить?\n1. Краски для стен и потолков\n2. Садовая мебель\n3. Двери\nСделайте выбор: ')
    if query == '1':
        query = 'kraski-dlya-sten-i-potolkov/'
    if query == '2':
        query = 'sadovaya-mebel/'
    if query == '3':
        query = 'dveri/'
    process.crawl(LmruSpider, query=query)
    process.start()
