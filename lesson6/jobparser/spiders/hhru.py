import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://rostov.hh.ru/search/vacancy?area=76&fromSearchLine=true&st=searchVacancy&text=Python&from=suggest_post']

    def parse(self, response:HtmlResponse):
        vacancies_links = response.xpath('//span[@class="g-user-content"]/a[@class="bloko-link"]/@href').extract()
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in vacancies_links:
            yield response.follow(link, callback=self.vacancy_parse)


    def vacancy_parse(self, response:HtmlResponse):
        name = response.css("h1::text").extract_first()
        salary = response.css("p.vacancy-salary span::text").extract()
        url = response.url
        yield JobparserItem(url=url, name=name, salary=salary)
