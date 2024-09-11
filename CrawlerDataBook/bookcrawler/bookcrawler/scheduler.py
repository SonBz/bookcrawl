# import logging
#
# from scrapy.crawler import CrawlerRunner
# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from twisted.internet import reactor
# from scrapy.utils.log import configure_logging
# from scrapy import cmdline
#
# from bookcrawler.spiders.goodreads import GoodreadsSpider
#
# logger = logging.getLogger(__name__)
#
# logging.basicConfig(
#     handlers=[logging.FileHandler('crawl.log', 'w', 'utf-8')],
#     format='%(levelname)s: %(message)s',
#     level=logging.DEBUG
# )
# def crawl_job():
#     settings = get_project_settings()
#     runner = CrawlerRunner(settings)
#     return runner.crawl(GoodreadsSpider)
#
#
# def schedule_next_crawl(null, hour):
#     """
#     Schedule the next crawl
#     """
#     # tomorrow = (datetime.datetime.now() + datetime.timedelta(days=20))\
#     #     .replace(hour=hour, minute=30, second=0, microsecond=0)
#     # sleep_time = (tomorrow - datetime.datetime.now()).total_seconds()
#     reactor.callLater(1, crawl)
#
#
# def crawl():
#     d = crawl_job()
#     d.addCallback(schedule_next_crawl, hour=13)
#     d.addErrback(catch_error)
#
#
# def catch_error(failure):
#     logger.error(failure.value)
#
#
# def run_spider_cmd():
#     print("Running spider")
#     cmdline.execute("scrapy crawl goodreads".split())
#
# if __name__ == "__main__":
#     # crawl()
#     # reactor.run()
#     run_spider_cmd()

# from crontab import CronTab
#
# cron = CronTab(user='Nguyen Son')
# job = cron.new(command='python test.py')
# job.minute.every(1)
# cron.write()

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from bookcrawler.spiders.goodreads import GoodreadsSpider


configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
def run_spiders():
    runner = CrawlerRunner(get_project_settings())

    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(GoodreadsSpider)
        reactor.stop()

    crawl()
    reactor.run()