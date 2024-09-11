# -*- coding: utf-8 -*-
import re, datetime, socket
from urllib.parse import urljoin

from math import ceil
from unidecode import unidecode
from ..items import BookLoader, GoodreadsBookItem
from scrapy.linkextractors import LinkExtractor
from scrapy.loader.processors import MapCompose
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import Join


class GoodreadsSpider(CrawlSpider):
    name = "goodreads"
    base_url = "https://www.goodreads.com"
    allowed_domains = ['www.goodreads.com']
    start_urls = [
        "https://www.goodreads.com/list/show/36946.S_ch_Vi_t_hay_nh_t"
    ]
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[@rel="next"]')),
    )
    mc = MapCompose(lambda i: urljoin('https://www.goodreads.com', i))

    def parse(self, response):
        print("Parse book: " + response.url)
        # Get the next page and yield Request
        next_selector = response.xpath(
            '//a[@rel="next"]//@href'
        )
        for url in next_selector.extract():
            print("Request url:" + url)
            yield response.follow(self.mc(url)[0], callback=self.parse)

        # Get url author
        url_author = response.xpath('//a[@class="authorName"]/@href')
        for url in url_author.getall():
            yield response.follow(url, callback=self.parse_author)

        # Get url user
        url_user = response.css('a.userPhoto::attr(href)')
        for url in url_user.getall():
            yield response.follow(url, callback=self.parse_user)

        # Get URL in page and yield Request
        url_selector = response.xpath(
            '//a[@class="bookTitle"]//@href'
        )

        for url in url_selector.extract():
            if ("/series/" in url):
                yield response.follow(url, callback=self.parse)
            elif ("/book/show/" in url):
                yield response.follow(url, callback=self.parse_book)

    # crawl book from  author
    def parse_author(self, response):
        if '/author/show' in response.url:
            more_book_url = response.xpath('//a[contains(.,"More books")]/@href').get()
            # Check more book by author
            if more_book_url:
                # Get url author/list
                yield response.follow(more_book_url, callback=self.parse_author)
            else:
                bookList = response.xpath('//a[@class="bookTitle"]/@href').getall()
                for bookUrl in bookList:
                    yield response.follow(bookUrl, callback=self.parse_book)

        # Crawl book from /author/list
        if '/author/list' in response.url:
            book_list = response.xpath('//a[@class="bookTitle"]/@href').getall()
            for book_url in book_list:
                yield response.follow(book_url, callback=self.parse_book)

            next_selector = response.xpath(
                '//a[@rel="next"]//@href'
            )
            for url in next_selector.extract():
                yield response.follow(url, callback=self.parse_author)

    # crawl book from user
    def parse_user(self, response):
        url_user = response.xpath('//a[@rel="acquaintance"]/@href')
        for url in url_user.getall():
            yield response.follow(url, callback=self.parse_user)

        # Get url review/list
        url_review = response.xpath('//div[@class="right"]/a[contains(.,"More…")]/@href').get()
        if url_review:
            yield response.follow(self.mc(url_review)[0], callback=self.parse_user)

        # crawl book and get url author
        if '?page=' in response.url:
            url_book_list = response.css('td.title>div.value>a::attr(href)')
            url_author_list = response.css('td.author>div.value>a::attr(href)')
            for url_book in url_book_list.getall():
                yield response.follow(url_book, callback=self.parse_book)
            #  Get url author
            for url_author in url_author_list.getall():
                yield response.follow(url_author, callback=self.parse_author)

        # next page in url review/list
        if 'review' in response.url:
            total_page = re.findall('\d+', response.xpath('//a[@class="selectedShelf"]/text()').get())
            for page in range(1, ceil(int(total_page[0]) / 30) + 1):
                url_page = response.url.split('?page=')
                yield response.follow(url_page[0] + '?page=%s' % (page), callback=self.parse_user)

    def parse_book(self, response):
        # print("Parse book item: " + response.url)
        loader = BookLoader(GoodreadsBookItem(), response=response)

        loader.add_css("name", "#bookTitle::text")
        loader.add_value(
            'name_unidecode',
            unidecode(loader.get_css("#bookTitle::text")[-1]),
        )
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
        loader.add_xpath('isbn', '//*[@itemprop="isbn"]/text()')

        loader.add_xpath('img_url', '//img[@id="coverImage"]/@src')
        loader.add_xpath('publisher_name', '//div[@id="details"]/div[contains(.,"Published")]/text()')

        # Information fields
        loader.add_value('url', response.url)
        loader.add_value('project', self.settings.get('BOT_NAME'))
        loader.add_value('spider', self.name)
        loader.add_value('server', socket.gethostname())
        loader.add_value('date', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.load_description(response, loader)
        yield loader.load_item()

    def load_description(self, response, loader):
        if response.xpath('//div[@id="description"]/span[@style="display:none"]/text()') != []:
            description_all = ''
            for description in loader.get_xpath('//div[@id="description"]//span[@style="display:none"]//text()'):
                description_all = description_all + description + '\n'
            return loader.add_value('description', description_all)
        else:
            return loader.add_xpath('description', '//div[@id="description"]/span/text()')
