import logging
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from bookcrawler.spiders.goodreads_author import GoodreadsAuthorSpider
from bookcrawler.spiders.goodreads import GoodreadsSpider

configure_logging(install_root_handler=False)
logging.basicConfig(
    # handlers=[logging.FileHandler('crawl.log', 'w', 'utf-8')],
    filename='crawl.log',
    format='%(levelname)s: %(message)s',
    level=logging.DEBUG
)


runner = CrawlerRunner(get_project_settings())
runner.crawl(GoodreadsSpider)
d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run()