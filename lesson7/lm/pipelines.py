# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class LmPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class LmPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except TypeError as e:
                    print(e)

    def item_completed(self, results, item, info):
        print()
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]

        # формируем характеристики
        new_item = {}
        count = 0
        while len(item['params'])/2 > count:
            new_item[item['params'][count]] = item['params'][int((len(item['params']) / 2 + count))]
            count += 1
        item['params'] = new_item
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        path_name = item['url'].split('/')[-2]
        photo_name = request.url.split('/')[-1]
        return f'{path_name}/{photo_name}'

