# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Join

def process_photo_links(photo_url):
    if photo_url.count('w_2000') >= 1:
        correct_url = photo_url
        return correct_url

def concat_params(params):
    #new_params = params.split('')
    new_params = params.replace('\n                ', '').replace('\n            ', '')
    print()
    return new_params

def price(price):
    new_price = int(price.replace(' ', ''))
    return new_price

class LmItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    params = scrapy.Field(input_processor=MapCompose(concat_params))
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(process_photo_links))
    price = scrapy.Field(input_processor=MapCompose(price), output_processor=TakeFirst())
    _id = scrapy.Field()
