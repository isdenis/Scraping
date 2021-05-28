# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from pprint import pprint


class InstagramSpider(scrapy.Spider):
    #атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login = ''
    insta_pwd = ''
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = ['ai_machine_learning', 'rostov_remont.161', 'rem_stroy_don']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = '5aefa9893005572d237da5068082d8d5'
    following_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'

    def parse(self, response: HtmlResponse):             #Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)   #csrf token забираем из html
        yield scrapy.FormRequest(                   #заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:                 #Проверяем ответ после авторизации
            for user in self.parse_user:
                yield response.follow(                  #Переходим на желаемую страницу пользователя.
                    f'/{user}/',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       #Получаем id пользователя
        variables = {'id': user_id,                                    #Формируем словарь для передачи даных в запрос
                     'first': 12}                                      #12 постов. Можно больше (макс. 50)
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'    #Формируем ссылку для получения данных
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}         #variables ч/з deepcopy во избежание гонок
        )
        yield response.follow(
            url_following,
            callback=self.user_following_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables):   #Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')     #Подписчики
        for followers in followers:                                                         #Перебираем подписчиков, собираем данные
            item = InstaparserItem(
                acc_name=username,
                user_name=followers['node']['username'],
                acc_id=user_id,
                photo=followers['node']['profile_pic_url'],
                user_id=followers['node']['id'],
                follower=followers['node'],
                whois='followers'
            )
        yield item                  #В пайплайн

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables):   #Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                url_following,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        following = j_data.get('data').get('user').get('edge_follow').get('edges')     #на которого подписан
        for following in following:                                                    #Перебираем на кого подписан, собираем данные
            item = InstaparserItem(
                acc_name=username,
                user_name=following['node']['username'],
                user_id=following['node']['id'],
                acc_id=user_id,
                photo=following['node']['profile_pic_url'],
                following=following['node'],
                whois='following'
            )
        yield item                  #В пайплайн
