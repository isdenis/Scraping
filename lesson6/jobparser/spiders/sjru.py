import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response):
        vacancies_links = response.xpath('//a[contains(@class, "icMQ_ _6AfZ9")]/@href').extract()
        print()
        next_page = response.xpath("//a[@rel='next']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in vacancies_links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response:HtmlResponse):
        name = response.css("h1::text").extract_first()
        salary = response.xpath("//span[@class='_1h3Zg _2Wp8I _2rfUm _2hCDz']/text()").extract()
        url = response.url
        yield JobparserItem(url=url, name=name, salary=salary)
