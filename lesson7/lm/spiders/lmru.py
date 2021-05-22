import scrapy
from scrapy.http import HtmlResponse
from lm.items import LmItem
from scrapy.loader import ItemLoader

class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super(LmruSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{query}']

    def parse(self, response:HtmlResponse):
        links = response.xpath("//a[@class='bex6mjh_plp b1f5t594_plp p5y548z_plp pblwt5z_plp nf842wf_plp']")
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in links:
            yield response.follow(link, callback=self.product_parse)


    def product_parse(self, response:HtmlResponse):
        loader = ItemLoader(item=LmItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photos', "//source[contains(@media, 'only screen and')]/@srcset")
        loader.add_xpath('params', "//dt[@class='def-list__term']/text()")
        loader.add_xpath('params', "//dd[@class='def-list__definition']/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('price', "//span[@slot='price']/text()")

        yield loader.load_item()
