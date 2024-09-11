# -*- coding: utf-8 -*-
import scrapy
import socket
import datetime
import re
from unidecode import unidecode
from ..items import AuthorItem, AuthorLoader, BookLoader, GoodreadsBookItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import TakeFirst, Join

from .goodreads_book import GoodreadsBookSpider

class GoodreadsAuthorSpider(CrawlSpider):
    name = "goodreads_author"
    start_urls = [
        # "https://www.goodreads.com/", 
        # "https://www.goodreads.com/author/on_goodreads",
        "https://www.goodreads.com/list/show/36946.S_ch_Vi_t_hay_nh_t",
        # "https://www.goodreads.com/author/show/4856561.T_Ho_i"
    ]

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[@rel="next"]')),
        Rule(
            LinkExtractor(restrict_xpaths='//a[contains(@href,"/author/show")]'),
            callback='parse_author',
        ),
    )

    def __init__(self):
        super().__init__()
        self.book_spider = GoodreadsBookSpider("bookcrawler")

    def parse(self, response):
        url = response.request.url
        print("Parse author: " + url)
        # Don't follow blog pages
        if "/blog?page=" in url:
            return

        if "/author/show/" in url:
            print("start crawl author")
            yield response.follow(url, callback=self.parse_author)

        # If an author crawl is enabled, we crawl similar authors for this author,
        # authors that influenced this author,
        # as well as any URL that looks like an author bio page
        influence_author_urls = response.css('div.dataItem>span>a[href*="/author/show"]::attr(href)').extract()

        for author_url in influence_author_urls:
            yield response.follow(author_url, callback=self.parse_author)

        similar_authors = response.css('a[href*="/author/similar"]::attr(href)').extract_first()

        if similar_authors:
            yield response.follow(similar_authors, callback=self.parse)

        all_authors_on_this_page = response.css('a[href*="/author/show"]::attr(href)').extract()
        for author_url in all_authors_on_this_page:
            yield response.follow(author_url, callback=self.parse_author)

    def parse_author(self, response):
        print("Parse item author: " + response.url)
        loader = AuthorLoader(AuthorItem(), response=response)
        loader.add_value('url', response.request.url)
        loader.add_css("name", 'h1.authorName>span[itemprop="name"]::text')
        loader.add_value(
            'name_unidecode',
            unidecode(",".join(loader.get_xpath('//h1[@class="authorName"]/span[@itemprop="name"]/text()'))),
        )
        loader.add_css("birth_date", 'div.dataItem[itemprop="birthDate"]::text')
        loader.add_css("death_date", 'div.dataItem[itemprop="deathDate"]::text')

        loader.add_css("genres", 'div.dataItem>a[href*="/genres/"]::text')
        loader.add_css("influences", 'div.dataItem>span>a[href*="/author/show"]::text')

        loader.add_css("avg_rating", 'span.average[itemprop="ratingValue"]::text')
        loader.add_css("num_reviews", 'span[itemprop="reviewCount"]::attr(content)')
        loader.add_css("num_ratings", 'span[itemprop="ratingCount"]::attr(content)')

        loader.add_css("about", 'div.aboutAuthorInfo')

        # Information fields
        loader.add_value('url', response.url)
        loader.add_value('project', self.settings.get('BOT_NAME'))
        loader.add_value('spider', self.name)
        loader.add_value('server', socket.gethostname())
        loader.add_value('date', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        loader.add_xpath('img_url', '//div[@class="leftContainer authorLeftContainer"]/a/img[@itemprop="image"]/@src')
        born_list = response.xpath('//div[@class="rightContainer"]/text()').getall()
        found = False
        if born_list is not None:
            for born in born_list:
                txt = born.lower().strip()
                txt = re.sub(r'[\t\n\r\f\v]', r'', txt)
                if txt == "":
                    continue
                txt = unidecode(txt)
                loader.add_value("born", txt)
                found = True
                if ("vietnam" in txt or "viet nam" in txt):
                    book_url = re.sub('/show/', '/list/', response.url)
                    print("book url:" + book_url)
                    yield response.follow(book_url, callback=self.book_spider.parse)
                break
        if not found:
            loader.add_value("born", "undefined")

        yield loader.load_item()

        similar_authors = response.css('a[href*="/author/similar"]::attr(href)').extract_first()

        if similar_authors:
            yield response.follow(similar_authors, callback=self.parse)

        print("Parse author finished: " + response.url)

        # return loader.load_item()
        # book_url = re.sub('/show/', '/list/', response.url)
        # yield response.follow(book_url, callback=self.book_spider.parse)
