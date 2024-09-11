# -*- coding: utf-8 -*-
import datetime
import scrapy
import socket
from urllib.parse import urljoin
import re

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from scrapy.http import Request
from ..items import TikiBookItem, BookLoader

from unidecode import unidecode



class TikiBookSpider(scrapy.Spider):
    name = "tiki"
    allowed_domains = ["tiki.vn"]
    start_urls = [
        "https://tiki.vn/sach-tieng-anh/c320",
        "https://tiki.vn/sach-truyen-tieng-viet/c316"
    ]

    mc = MapCompose(lambda i: urljoin('http://tiki.vn', i))

    def parse(self, response):
        # Get the next page and yield request
        next_selector = response.xpath('//*[@class="next"]/@href')

        for url in next_selector.extract():
            yield Request(self.mc(url)[0])

        # Get URL in page and yield Request
        url_selector = response.xpath('//*[@class="product-item    "]/a/@href')
        for url in url_selector.extract():
            yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        """
        @url https://tiki.vn/khoang-cach-p1044532.html
        @returns items 1
        @scrapes name name_unidecode price description
        @scrapes url project spider server date
        """
        loader = BookLoader(item=TikiBookItem(), response=response)

        loader.add_xpath('name', '//*[@class="item-name"]/span/text()')
        loader.add_xpath('name_unidecode','//*[@class="item-name"]/span/text()',
            MapCompose(unidecode, str.strip, str.title),
        )

        loader.add_value(
            'author',
            filter(
                None,
                [
                    str.strip(i)
                    for i in loader.get_xpath('//div[@class="brand-block-row"]/div[@class="item-brand"]'
                                              '//a[contains(@href,"/author")]/text()')
                ],
            ),
            Join(','),
        )
        loader.add_value(
            'author_unidecode',
            filter(
                None,
                [
                    unidecode(str.strip(i))
                    for i in loader.get_xpath('//div[@class="brand-block-row"]/div[@class="item-brand"]'
                                              '//a[contains(@href,"/author")]/text()')
                ],
            ),
            Join(','),
        )
        loader.add_value(
            "author_url",
            filter(
                None,
                [
                    str.strip(self.mc(i)[0])
                    for i in loader.get_xpath('//div[@class="brand-block-row"]/div[@class="item-brand"]'
                                              '//a[contains(@href,"/author")]/@href')
                ],
            ),
            Join(','),
        )
        loader.add_css('publish_date','[rel=publication_date]+td.last::text')
        loader.add_css('isbn', '[rel=isbn13]+td.last::text')
        loader.add_css('num_pages', '[rel=number_of_page]+td.last::text')
        loader.add_css('format', '[rel=book_cover]+td.last::text')
        loader.add_css('publisher_name', '[rel=manufacturer_book_vn]+td.last::text')
        loader.add_css('dimensions', '[rel=dimensions]+td.last::text')
        loader.add_css('manufacturer', '[rel=publisher_vn]+td.last>a::text')
        loader.add_css('sku', '[rel=sku]+td.last::text')
        loader.add_css('translators', '[rel=dich_gia]+td.last::text')
        loader.add_css('avg_rating', '[itemprop=ratingValue]::attr(content)')
        loader.add_css('num_ratings', '[itemprop=ratingCount]::attr(content)')
        loader.add_xpath(
            'price',
            '//*[@id="span-price"]/text()',
            TakeFirst(),
            re=r'\d+\.\d+',
        )
        loader.add_value(
            'description',
            [
                re.sub('<[^<]+?>', '', i)
                for i in loader.get_xpath('//*[@id="gioi-thieu"]/p')
            ],
            Join('\n'),
        )
        loader.add_xpath('img_url', '//*[@itemprop="image"]/@src')

        # # Information fields
        loader.add_value('url', response.url)
        loader.add_value('project', self.settings.get('BOT_NAME'))
        loader.add_value('spider', self.name)
        loader.add_value('server', socket.gethostname())
        loader.add_value('date', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        yield loader.load_item()