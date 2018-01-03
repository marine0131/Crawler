# -*- coding: utf-8 -*-
import scrapy
import requests
import re
import time
import copy
from lxml import etree
from ..items import LianjiaItem
from scrapy_redis.spiders import RedisSpider

class LianjiaSpider(RedisSpider):
    name = 'lianjiaspider'
    redis_key = 'lianjiaspider:urls'
    start_urls = 'http://hz.lianjia.com/ershoufang/'
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2306.400 QQBrowser/9.5.10648.400'
    my_district = ['yuhang']

    def start_requests(self):
        # user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
        #                 Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': self.user_agent}
        yield scrapy.Request(url=self.start_urls, headers=headers, method='GET', callback=self.parse, errback=self.err, dont_filter=True)

    def err(self):
        print("request error!!!")

    def parse(self, response):
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 \
                                 Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': user_agent}
        lists = response.body.decode('utf-8')
        selector = etree.HTML(lists)
        area_list = selector.xpath('/html/body/div[3]/div[1]/dl[2]/dd/div[1]/div/a')

        my_area_list = copy.copy(area_list)
        for i, area in enumerate(area_list):
            area_pin = area.xpath('@href').pop().split('/')[2]   # pinyin
            if not area_pin in self.my_district:
                my_area_list.remove(area)

        for area in my_area_list:
            try:
                area_han = area.xpath('text()').pop()    # locate
                area_pin = area.xpath('@href').pop().split('/')[2]   # pinyin
                area_url = 'http://hz.lianjia.com/ershoufang/{}/'.format(area_pin)
                print(area_url)
                yield scrapy.Request(url=area_url, headers=headers, callback=self.detail_url, meta={"id1":area_han,"id2":area_pin}, dont_filter=True)
            except Exception:
                pass

    def get_latitude(self,url):
        p = requests.get(url)
        contents = etree.HTML(p.content.decode('utf-8'))
        latitude = contents.xpath('/html/body/script[20]/text()').pop()
        time.sleep(3)
        regex = '''resblockPosition(.+)'''
        items = re.search(regex, latitude)
        content = items.group()[:-1]  # lattitude
        longitude_latitude = content.split(':')[1]
        return longitude_latitude[1:-1]

    def detail_url(self,response):
        for i in range(1,50):
            url = 'http://hz.lianjia.com/ershoufang/{}/pg{}/'.format(response.meta["id2"],str(i))
            print(url)
            time.sleep(2)
            try:
                contents = requests.get(url)
                contents = etree.HTML(contents.content.decode('utf-8'))
                houselist = contents.xpath('/html/body/div[4]/div[1]/ul/li')
                for house in houselist:
                    try:
                        item = LianjiaItem()
                        item['title'] = house.xpath('div[1]/div[1]/a/text()').pop()
                        item['community'] = house.xpath('div[1]/div[2]/div/a/text()').pop()
                        item['model'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[1]
                        item['area'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[2]
                        item['focus_num'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[0]
                        item['watch_num'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[1]
                        item['time'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[2]
                        item['price'] = house.xpath('div[1]/div[6]/div[1]/span/text()').pop()
                        item['average_price'] = house.xpath('div[1]/div[6]/div[2]/span/text()').pop()
                        item['link'] = house.xpath('div[1]/div[1]/a/@href').pop()
                        item['city'] = response.meta["id1"]
                        # self.url_detail = house.xpath('div[1]/div[1]/a/@href').pop()
                        # item['Latitude'] = self.get_latitude(self.url_detail)
                    except Exception:
                        pass
                    yield item
            except Exception:
                pass
