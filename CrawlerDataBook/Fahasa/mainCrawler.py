# -*- coding: utf-8 -*-
import json,codecs
from datetime import datetime
from bs4 import BeautifulSoup
from processor import processor, crawlerData
from link_crawler import MC_FILE_OUTPUT,MC_FILE_OUTPUT_SN,MC_FILE_INPUT_CATEGORYID


# class MainCrawler:
#     create_date = datetime.now()
#     logger = processor().getLogging()
#     logger.info('======== RUN CRAWL FAHASA DATA-' + str(create_date) + ' =========')
#     processor().writerTitle(MC_FILE_OUTPUT)
#     processor().writerTitleBasic(MC_FILE_OUTPUT_SN)
#     categoryList = processor().readFile(MC_FILE_INPUT_CATEGORYID)
#     count = 1;
#     for categoryIdx in range(11,len(categoryList)):
#         category_id = categoryList[categoryIdx][0]
#         page = 1;
#         while page > 0:
#             for i in range(0,3):
#                 link_crawler = "https://www.fahasa.com/fahasa_catalog/product/loadproducts?" \
#                                "category_id=%d&currentPage=%d&limit=24&order=num_orders"%(int(category_id),page)
#                 try:
#                     resultHtml = processor().readWebCookie(link_crawler)
#                     stringHtml = str(resultHtml)
#                     jsonWeb = json.loads(stringHtml)
#                     break
#                 except Exception as error:
#                     if i == 2:
#                         logger.error("MC1 :" + str(error))
#                         break
#                     else:
#                         i += 1
#                         logger.info("Retry Link:"+str(i))
#                         continue
#             try:
#                 noofpages = jsonWeb['noofpages']
#             except Exception as  error :
#                 logger.error("MC2 :Link error add cookies")
#                 continue
#
#             if page == int(noofpages):
#                 logger.info("MC3-End Page:"+str(page))
#                 break
#             page += 1
#             product_list = jsonWeb['product_list']
#             for detailProduct in product_list:
#                 logger.info("product :" + str(count))
#                 nameBook = detailProduct['product_name']
#                 linkBook = detailProduct['product_url']
#                 piceBook = detailProduct['product_price']
#                 imgBook = detailProduct['image_src']
#                 try:
#                     bookHtml = processor().readWebCookie(linkBook)
#                     soup_html = BeautifulSoup(bookHtml, 'html.parser')
#                 except Exception as error:
#                     logger.error("MC2:" + str(error))
#                     break
#                 book = crawlerData().dataWeb(soup_html, linkBook, nameBook, imgBook)
#                 if book == -1:
#                     continue
#                 try:
#                     dataSplit = bookHtml.split('Suggestion(SESSION_ID, "Product View",')
#                     dataScript = dataSplit[1].split(");\n    });\n</script>\n")
#                 except Exception as error:
#                     logger.error("MC3 :"+str(error))
#                     continue
#                 jsonConvert = json.loads(dataScript[0])
#                 items = jsonConvert["items"]
#                 language = items[0]["category_main"]
#                 category = categoryList[categoryIdx][1]
#                 bookBasic = crawlerData().dataWebBasic(book,category,language,piceBook)
#                 processor().writeFileBook(MC_FILE_OUTPUT, count, book,language,category)
#                 processor().writeFileBookBasic(MC_FILE_OUTPUT_SN, count, bookBasic)
#                 count += 1
class MainCrawler:
    link_crawler = "https://www.fahasa.com/fahasa_catalog/product/loadproducts?" \
                   "category_id=%d&currentPage=%d&limit=24&order=num_orders" % (int(category_id), page)

    resultHtml = processor().readWebCookie(link_crawler)
    for categoryIdx in range(11,len(categoryList)):
        category_id = categoryList[categoryIdx][0]
        page = 1;
        while page > 0:
            for i in range(0,3):
                link_crawler = "https://www.fahasa.com/fahasa_catalog/product/loadproducts?" \
                               "category_id=%d&currentPage=%d&limit=24&order=num_orders"%(int(category_id),page)
                try:
                    resultHtml = processor().readWebCookie(link_crawler)
                    stringHtml = str(resultHtml)
                    jsonWeb = json.loads(stringHtml)
                    break
                except Exception as error:
                    if i == 2:
                        logger.error("MC1 :" + str(error))
                        break
                    else:
                        i += 1
                        logger.info("Retry Link:"+str(i))
                        continue
            try:
                noofpages = jsonWeb['noofpages']
            except Exception as  error :
                logger.error("MC2 :Link error add cookies")
                continue

            if page == int(noofpages):
                logger.info("MC3-End Page:"+str(page))
                break
            page += 1
            product_list = jsonWeb['product_list']
            for detailProduct in product_list:
                logger.info("product :" + str(count))
                nameBook = detailProduct['product_name']
                linkBook = detailProduct['product_url']
                piceBook = detailProduct['product_price']
                imgBook = detailProduct['image_src']
                try:
                    bookHtml = processor().readWebCookie(linkBook)
                    soup_html = BeautifulSoup(bookHtml, 'html.parser')
                except Exception as error:
                    logger.error("MC2:" + str(error))
                    break
                book = crawlerData().dataWeb(soup_html, linkBook, nameBook, imgBook)
                if book == -1:
                    continue
                try:
                    dataSplit = bookHtml.split('Suggestion(SESSION_ID, "Product View",')
                    dataScript = dataSplit[1].split(");\n    });\n</script>\n")
                except Exception as error:
                    logger.error("MC3 :"+str(error))
                    continue
                jsonConvert = json.loads(dataScript[0])
                items = jsonConvert["items"]
                language = items[0]["category_main"]
                category = categoryList[categoryIdx][1]
                bookBasic = crawlerData().dataWebBasic(book,category,language,piceBook)
                processor().writeFileBook(MC_FILE_OUTPUT, count, book,language,category)
                processor().writeFileBookBasic(MC_FILE_OUTPUT_SN, count, bookBasic)
                count += 1




