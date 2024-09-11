# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import pymongo
import ssl

from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)

BOOK_TYPE = 0
AUTHOR_TYPE = 1
PPDVN_TYPE = 2

class BookcrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):

    collection_name = ['books', 'authors', 'ppdvn']

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.types = ["book", "author", "ppdvn"]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'books'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri,ssl_cert_reqs=ssl.CERT_NONE)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # item_type = type(item).__name__.replace("Item", "").lower()
        item_type = item.item_type
        if item_type == self.types[BOOK_TYPE]:
            self.process_book_item(item, spider)
        elif item_type == self.types[AUTHOR_TYPE]:
            self.process_author_item(item, spider)
        elif item_type == self.types[PPDVN_TYPE]:
            self.process_ppdvn_item(item, spider)


    def process_book_item(self, item, spider):
        collection = self.db[self.collection_name[BOOK_TYPE]]
        is_valid = True
        for data in item:
            if not data:
                is_valid = False
                raise DropItem("Missing %s!" % data)

        if is_valid:
            if collection.find(
                {
                    'url': item['url'],
                    'name_unidecode': item['name_unidecode'],
                    'spider': spider.name,
                }
            ).count() != 0:
                raise DropItem("Item existed")

            else:
                collection.insert({k: v for k, v in dict(item).items()})
                logger.info("Book added to MongoDB database!")
                return item

    def process_author_item(self, item, spider):
        collection = self.db[self.collection_name[AUTHOR_TYPE]]
        is_valid = True
        for data in item:
            if not data:
                is_valid = False
                raise DropItem("Missing %s!" % data)

        if is_valid:
            if collection.find(
                {
                    'url': item['url'],
                    'name_unidecode': item['name_unidecode'],
                    'spider': spider.name,
                }
            ).count() != 0:
                raise DropItem("Item existed")

            else:
                collection.insert({k: v for k, v in dict(item).items()})
                logger.info("Author added to MongoDB database!")
                return item

    def process_ppdvn_item(self, item, spider):
        collection = self.db[self.collection_name[PPDVN_TYPE]]
        is_valid = True
        for data in item:
            if not data:
                is_valid = False
                raise DropItem("Missing %s!" % data)

        if is_valid:
            if collection.find(
                    {
                        'isbn': item['isbn'],
                        'name_unidecode': item['name_unidecode'],
                        'spider': spider.name,
                    }
            ).count() != 0:
                raise DropItem("Item existed")

            else:
                collection.insert({k: v for k, v in dict(item).items()})
                logger.info("Ppdvn added to MongoDB database!")
                return item