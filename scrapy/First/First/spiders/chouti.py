# -*- coding: utf-8 -*-
import scrapy
import io
import sys
from scrapy.selector import Selector,XmlXPathSelector
from scrapy.http import Request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')

class ChoutiSpider(scrapy.Spider):
    name = 'chouti'
    allowed_domains = ['chouti.com']
    start_urls = ['http://dig.chouti.com/']

    def parse(self, response):
        ''''''
        hxs = Selector(response=response)
        item_list = hxs.xpath("//div[@id='content-list']/div[@class='item']")
        # content = item_list[0].xpath("./div[@class='news-content']//a/text()").extract()
        for item in item_list:
            content = item.xpath("./div[@class='news-content']//a/text()").extract_first()
            print(content.strip())
        page_list = hxs.xpath("//div[@id='dig_lcpage']//a/@href").extract()
        for page in page_list:
            page_url = 'http://dig.chouti.com' +  page
            yield Request(url=page_url)
