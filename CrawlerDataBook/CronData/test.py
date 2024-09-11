# -*- coding: utf-8 -*-
import datetime, time
from datetime import datetime
from PPDVN.processor import processor
from PPDVN.FuncCrawlerPppdvn import CrawlerPppdvn
import schedule

def crawl_schedule():
    create_date = datetime.now()
    logger = processor().getLogging()
    logger.info('======== RUN CRON CRAWLER DATA-'+str(create_date)+' =========')
    name_table_publiher = 'ppdvn_gov_vn'
    name_table_not_publisher = 'ppdvn_not_publish'
    for page in range(1,2) :
        result_publiser = CrawlerPppdvn().crawler_publisher(page,name_table_publiher)
        page += 1
        if result_publiser == -1:
            logger.info("stop crawler publisher")
            break
    for page in range(1,2):
        result_not_publisher = CrawlerPppdvn().crawler_not_publisher(page,name_table_not_publisher)
        page += 1
        if result_not_publisher == -1:
            logger.info("stop crawler not publisher")


crawl_schedule()
# schedule.every().thursday.at("09:37").do(crawl_schedule)
# while True:
#     schedule.run_pending()
#     time.sleep(1)