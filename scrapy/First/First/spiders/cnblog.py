# -*- coding: utf-8 -*-
import scrapy


class CnblogSpider(scrapy.Spider):
    name = 'cnblog'
    allowed_domains = ['cnblogs.com']
    start_urls = ['http://cnblogs.com/']

    def parse(self, response):
        pass
