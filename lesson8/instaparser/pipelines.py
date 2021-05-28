# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient

class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.insta

    def process_item(self, item, spider):
        collection = self.mongo_base['parse']
        insta = {}
        insta['acc_id'] = item['acc_id']
        insta['acc_name'] = item['acc_name']
        insta['user_id'] = item['user_id']
        insta['user_name'] = item['user_name']
        insta['photo'] = item['photo']
        insta['whois'] = item['whois']
        collection.insert_one(insta)
        return item


def search_follow():
    client = MongoClient('localhost', 27017)
    db = client['insta']
    instag = db.parse

    name = input('Введите имя аккаунта: ')
    follow = input('Что ищем? 1 - на кого подписан, 2 - кто в подписчиках:  ')
    if follow == '1':
        follow = 'following'
    if follow == '2':
        follow = 'followers'

    for search in instag.find({'acc_name': name, 'whois': follow}):
        print(search)

