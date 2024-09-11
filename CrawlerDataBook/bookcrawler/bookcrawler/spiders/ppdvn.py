import datetime, socket, re, scrapy
from builtins import print

from unidecode import unidecode
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import TakeFirst, Join
from scrapy.linkextractors import LinkExtractor
from ..items import PPDVNLoader, PPDVNPublishedItem , PPDVNNotPublishedItem
from scrapy.selector import Selector

PUBLISHED = 1
NOT_PUBLISHED = 0
SELF_PUBLISHED = 1
NOT_SELF_PUBLISHED = 0

class PPDVNSpiders(CrawlSpider):
    name = "ppdvn"
    base_url = "https://ppdvn.gov.vn"
    allowed_domains = ['ppdvn.gov.vn']
    start_urls = [
        'https://ppdvn.gov.vn/web/guest/tra-cuu-luu-chieu',
        'https://ppdvn.gov.vn/web/guest/ke-hoach-xuat-ban'
    ]

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a[contains(.,"Trang sau")]'),
             callback='parse_item', follow=True),
    )

    def parse(self, response):

        next_selector = response.xpath('//a[contains(.,"Trang cuối")]/@href').get()
        if 'tra-cuu-luu-chieu' in next_selector:
            totalPage = int(next_selector.split("=")[1])
            for page in range(totalPage):
                link = next_selector.replace(str(totalPage), str(page + 1))
                yield response.follow(self.base_url + link, callback=self.parse_published)

        if 'ke-hoach-xuat-ban' in next_selector:
            totalPage = int(next_selector.split("=")[1])
            for page in range(totalPage):
                link = next_selector.replace(str(totalPage), str(page + 1))
                yield response.follow(self.base_url + link, callback=self.parse_not_published)

    def parse_published(self, response):

        table = response.xpath('//div[@id="list_data_return"]//tr').getall()

        for index, row in enumerate(table[1:len(table)]) :
            loader = PPDVNLoader(PPDVNPublishedItem(), response=response)
            sel = Selector(text=row)

            loader.add_value('name', sel.xpath('//td[3]/text()').get())
            loader.add_value('name_unidecode', sel.xpath('//td[3]/text()').get())
            loader.add_value('author', sel.xpath('//td[4]/text()').get())
            loader.add_value('author_unidecode', sel.xpath('//td[4]/text()').get())
            # check isbn
            if sel.xpath('//td[2]/text()').get() is not None:
                loader.add_value('isbn', sel.xpath('//td[2]/text()').get())
            else:
                continue
            loader.add_value('editors', sel.xpath('//td[5]/text()').get())
            loader.add_value('editors_unidecode', sel.xpath('//td[5]/text()').get())
            loader.add_value('publisher_name', sel.xpath('//td[6]/text()').get())
            loader.add_value('associate_partner', sel.xpath('//td[7]/text()').get())
            loader.add_value('print_location', sel.xpath('//td[8]/text()').get())
            loader.add_value('date_lc', sel.xpath('//td[9]/text()').get())
            loader.add_value('status', PUBLISHED)

            loader.add_value('url', response.url)
            loader.add_value('project', self.settings.get('BOT_NAME'))
            loader.add_value('spider', self.name)
            loader.add_value('server', socket.gethostname())
            loader.add_value('date', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

            yield  loader.load_item()

    def parse_not_published(self, response):
        table = response.xpath('//div[@id="list_data_return"]//tr').getall()

        for index, row in enumerate(table[1:len(table)]):
            loader = PPDVNLoader(PPDVNNotPublishedItem(), response=response)
            sel = Selector(text=row)
            loader.add_value('name', sel.xpath('//td[3]/text()').get())
            loader.add_value('name_unidecode', sel.xpath('//td[3]/text()').get())
            loader.add_value('author', sel.xpath('//td[4]/text()').get())
            loader.add_value('author_unidecode', sel.xpath('//td[4]/text()').get())
            # check isbn
            if sel.xpath('//td[2]/text()').get() is not None:
                loader.add_value('isbn', sel.xpath('//td[2]/text()').get())
            else:
                continue
            loader.add_value('translators', sel.xpath('//td[5]/text()').get())
            loader.add_value('number_of_print', sel.xpath('//td[6]/text()').get())
            loader.add_value('associate_partner', sel.xpath('//td[8]/text()').get())
            loader.add_value('registration_number', sel.xpath('//td[9]/text()').get())
            if sel.xpath('//td[7]/text()').get() != ' ':
                loader.add_value('self_publish', SELF_PUBLISHED)
            else:
                loader.add_value('self_publish', NOT_SELF_PUBLISHED)

            loader.add_value('status', NOT_PUBLISHED)
            loader.add_value('url', response.url)
            loader.add_value('project', self.settings.get('BOT_NAME'))
            loader.add_value('spider', self.name)
            loader.add_value('server', socket.gethostname())
            loader.add_value('date', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
            yield loader.load_item()