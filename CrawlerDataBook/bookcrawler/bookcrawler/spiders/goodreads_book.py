# -*- coding: utf-8 -*-
import scrapy
import socket
import datetime
import re

from unidecode import unidecode
from ..items import AuthorItem, AuthorLoader, BookItem, BookLoader, GoodreadsBookItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.loader.processors import TakeFirst, Join

class GoodreadsBookSpider(CrawlSpider):
    name = "goodreads_book"
    base_url = "https://www.goodreads.com"
    allowed_domains = ['www.goodreads.com']
    start_urls = [
        # "https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh",
        # "https://www.goodreads.com/author/list/19229881.Beautiful_Mind_Vietnam",
        "https://www.goodreads.com/list/show/36946.S_ch_Vi_t_hay_nh_t"
    ]
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[@rel="next"]')),
        Rule(
            LinkExtractor(restrict_xpaths='//*[@class="bookTitle"]'),
            callback='parse_item',
        ),
    )
    def __init__(self, bot_name):
        super().__init__()
        self.bot_name = bot_name

    def parse(self, response):
        print("Parse book: " + response.url)
        # Get the next page and yield Request
        next_selector = response.xpath(
            '//a[@rel="next"]//@href'
        )
        for url in next_selector.extract():
            print("Request url:" + url)
            yield response.follow(url, callback=self.parse)

        # Get URL in page and yield Request
        url_selector = response.xpath(
            '//a[@class="bookTitle"]//@href'
        )
        for url in url_selector.extract():
            if ("/series/" in url):
                yield response.follow(url, callback=self.parse)
            elif ("/book/show/" in url):
                yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response):
        print("Parse book item: " + response.url)
        loader = BookLoader(GoodreadsBookItem(), response=response)

        loader.add_css("name", "#bookTitle::text")
        loader.add_value(
            'name_unidecode',
            unidecode(loader.get_css("#bookTitle::text")[-1]),
        )
        # loader.add_css("author", "a.authorName>span::text")
        # loader.add_xpath("author", '//a[@class="authorName"]/span[@itemprop="name"]/text()')
        loader.add_value(
            "author",
            filter(
                None,
                [
                    str.strip(i)
                    for i in loader.get_xpath('//a[@class="authorName"]/span[@itemprop="name"]/text()')
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
                    for i in loader.get_xpath('//a[@class="authorName"]/span[@itemprop="name"]/text()')
                ],
            ),
            Join(','),
        )
        # loader.add_css("author_url", 'a.authorName::attr(href)')
        loader.add_value(
            "author_url",
            filter(
                None,
                [
                    str.strip(i)
                    for i in loader.get_xpath('//a[@class="authorName"][@itemprop="url"]/@href')
                ],
            ),
            Join(','),
        )

        loader.add_css("num_ratings", "[itemprop=ratingCount]::attr(content)")
        loader.add_css("num_reviews", "[itemprop=reviewCount]::attr(content)")
        loader.add_css("avg_rating", "span[itemprop=ratingValue]::text")
        loader.add_css("num_pages", "span[itemprop=numberOfPages]::text")

        loader.add_css("language", "div[itemprop=inLanguage]::text")
        loader.add_css('publish_date', 'div.row::text')
        loader.add_css('publish_date', 'nobr.greyText::text')

        loader.add_css('original_publish_year', 'nobr.greyText::text')

        loader.add_css("genres", 'div.left>a.bookPageGenreLink[href*="/genres/"]::text')
        loader.add_css("awards", "a.award::text")
        loader.add_css('characters', 'a[href*="/characters/"]::text')
        loader.add_css('places', 'div.infoBoxRowItem>a[href*=places]::text')
        loader.add_css('series', 'div.infoBoxRowItem>a[href*="/series/"]::text')
        # loader.add_css('asin', 'div.infoBoxRowItem[itemprop=isbn]::text')
        # loader.add_css('isbn', 'div.infoBoxRowItem>span[itemprop=isbn]::text')
        # loader.add_xpath('asin', '//div[@itemprop="isbn"]/text()')
        loader.add_xpath('isbn', '//*[@itemprop="isbn"]/text()')
        # loader.add_css('rating_histogram', 'script[type*="protovis"]::text')

        loader.add_xpath('img_url', '//img[@id="coverImage"]/@src')

        # Information fields
        loader.add_value('url', response.url)
        loader.add_value('project', self.bot_name)
        loader.add_value('spider', self.name)
        loader.add_value('server', socket.gethostname())
        loader.add_value('date', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

        yield loader.load_item()