# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        if spider.name == 'hhru':
            hh = {}
            hh['name'] = item['name']
            hh['url'] = item['url']
            if item['salary'][0] == 'от ' and item['salary'][2] == ' до ':
                hh['sal_min'] = int(item['salary'][1].replace('\xa0', ''))
                hh['sal_max'] = int(item['salary'][3].replace('\xa0', ''))
                hh['sal_curr'] = item['salary'][5]
            if item['salary'][0] == 'от ' and item['salary'][2] != ' до ':
                hh['sal_min'] = None
                hh['sal_max'] = int(item['salary'][1].replace('\xa0', ''))
                hh['sal_curr'] = item['salary'][3]
            if item['salary'][0] == 'до ':
                hh['sal_min'] = None
                hh['sal_max'] = int(item['salary'][1].replace('\xa0', ''))
                hh['sal_curr'] = item['salary'][3]
            if item['salary'][0] == 'з/п не указана':
                hh['sal_min'] = None
                hh['sal_max'] = None
                hh['sal_curr'] = None
            collection.insert_one(hh)

        if spider.name == 'sjru':
            sj = {}
            sj['name'] = item['name']
            sj['url'] = item['url']
            if len(item['salary']) == 1:
                sj['sal_min'] = None
                sj['sal_max'] = None
                sj['sal_curr'] = None
            if len(item['salary']) == 4 and item['salary'][0] not in ['от', 'до', 'По договорённости']:
                sj['sal_min'] = int(item['salary'][0].replace('\xa0', ''))
                sj['sal_max'] = int(item['salary'][1].replace('\xa0', ''))
                sj['sal_curr'] = item['salary'][3]
            if item['salary'][0] == 'от':
                sj['sal_min'] = int(item['salary'][2].replace('\xa0', '').replace('руб.', ''))
                sj['sal_max'] = None
                sj['sal_curr'] = 'руб.'
            if item['salary'][0] == 'до':
                sj['sal_min'] = None
                sj['sal_max'] = int(item['salary'][2].replace('\xa0', '').replace('руб.', ''))
                sj['sal_curr'] = 'руб.'
            if len(item['salary']) == 3 and item['salary'][0] not in ['от', 'до']:
                sj['sal_min'] = None
                sj['sal_max'] = int(item['salary'][0].replace('\xa0', ''))
                sj['sal_curr'] = 'руб.'
            collection.insert_one(sj)
        return item
