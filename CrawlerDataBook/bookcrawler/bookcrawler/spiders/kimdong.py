import datetime, socket
from unidecode import unidecode
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import TakeFirst, Join
from scrapy.linkextractors import LinkExtractor
from ..items import KimDongBookItem, BookLoader
from scrapy.http import Request

class KimDongBookSpiders(CrawlSpider):
    name = "kimdong"
    base_url = "https://www.nxbkimdong.com.vn"
    allowed_domains = ['www.nxbkimdong.com.vn']
    start_urls = [
        'https://www.nxbkimdong.com.vn/lich-su-truyen-thong',
        'https://www.nxbkimdong.com.vn/wings-books',
        'https://www.nxbkimdong.com.vn/kien-thuc-khoa-hoc',
        'https://www.nxbkimdong.com.vn/van-hoc-viet-nam-0',
        'https://www.nxbkimdong.com.vn/van-hoc-nuoc-ngoai-0',
        'https://www.nxbkimdong.com.vn/truyen-tranh-0',
        'https://www.nxbkimdong.com.vn/manga-comic-0',
        'https://www.nxbkimdong.com.vn/sach-theo-do-tuoi',
        # 'https://www.nxbkimdong.com.vn/sach-moi'
    ]

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//li[@class="next"]//a')),
        Rule(LinkExtractor(restrict_xpaths='//*[@class="c-product-item--title-container"]//a'),
             callback='parse_item')
    )

    def parse_item(self, response):
        loader = BookLoader(item=KimDongBookItem(), response=response)

        loader.add_value('name',loader.get_xpath('//div[@class="clear-fix"]/div/div/div/text()')[-1])
        loader.add_value(
            'name_unidecode',
            unidecode(loader.get_xpath('//div[@class="clear-fix"]/div/div/div/text()')[-1]),
        )
        loader.add_value(
            'author',
            filter(
                None,
                [
                    str.strip(i)
                    for i in loader.get_css('div.field-name-field-product-tacgia>div>div>a::text')
                ]
            ),
            Join(','),
        )
        loader.add_value(
            'author_unidecode',
            filter(
                None,
                [
                    unidecode(str.strip(i))
                    for i in loader.get_css('div.field-name-field-product-tacgia>div>div>a::text')
                ],
            ),
            Join(','),
        )
        loader.add_value(
            "author_url",
            filter(
                None,
                [
                    str.strip(str(self.allowed_domains[0])+i)
                    for i in loader.get_css('div.field-name-field-product-tacgia>div>div>a::attr(href)')
                ],
            ),
            Join(','),
        )
        loader.add_value('description',loader.get_css('div.field-name-field-product-gioithieu>div>div>p::text'))
        loader.add_value('price',loader.get_xpath('//div[@class="gia-cost"]/span/text()'))
        loader.add_value('image_uri',loader.get_xpath('//div[@class="main-product-image"]/img[@class="img-responsive"]/@src'))
        loader.add_value('image_uri', loader.get_xpath('//img[@class="img-responsive"]/@data-src'))

        loader.add_css('num_pages','div.field-name-field-product-sotrang>div>div::text')
        loader.add_css('publish_date', 'div.field-name-field-product-phathanh>div>div>span::text')
        loader.add_css('isbn', 'div.field-name-field-product--isbn>div>div::text')
        loader.add_css('format', 'div.field-name-field-product-loaibia>div>div::text')
        loader.add_css('weight', 'div.field-name-field-product-trongluong>div>div::text')
        loader.add_css('series', 'div.field-name-field-product-tax-bosach>div>div>a::text')
        # series_list = response.css('div.field-name-field-product-tax-bosach>div>div>a::attr(href)').getall()
        # if series_list :
        #     for url in series_list:
        #         yield Request(url, callback=self.parse_item)
        # loader.add_css('books_url', 'div.field-name-field-product-tax-bosach>div>div>a::attr(href)')

        # Information fields
        loader.add_value('url', response.url)
        loader.add_value('project', self.settings.get('BOT_NAME'))
        loader.add_value('spider', self.name)
        loader.add_value('server', socket.gethostname())
        loader.add_value('date', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

        yield loader.load_item()

