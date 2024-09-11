# -*- coding: utf-8 -*-
import sys, re, csv, logging, requests ,configparser, os
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import ssl
from string_parser import cleanDisplayTitle, cleanSearchTitle
from unidecode import unidecode
from ClassBook import Book,BookBasic


class processor:

    def readHtml(self, link):
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        gcontext = ssl.SSLContext()
        page = urlopen(req, timeout=120, context=gcontext).read()
        soup_html = BeautifulSoup(page, 'html.parser')
        return soup_html

    def readWebCookie(self,link):
        parser = configparser.RawConfigParser()
        parser.read('config.ini')
        section_config = 'cookies'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
                   'Accept':'application/json, text/javascript, */*; q=0.01',
                   'Cookie': parser.get(section_config,'cookies')}
        content = requests.get(link, headers=headers)
        return  content.text

    def writeFileBook(self, filename, no, book,language,category):
        f = csv.writer(open(filename, 'a', encoding="utf-8", newline=''))
        title = book.title
        titleOriginal = book.titleOriginal
        titleLowerCase = book.titleLowerCase
        titleNoMark = book.titleNoMark
        titleTail = book.titleTail
        authorName = book.authorName
        authorNomark = book.authorNomark
        # authorLink = book.authorLink
        translator = book.translator
        imgLink = book.imgLink
        # manufacturer = book.manufacturer
        publisher = book.publisher
        isbn_10 = book.isbn_10
        isbn_13 = book.isbn_13
        numOfPages = book.numOfPages
        publishDate = book.publishDate
        # bookSize = book.bookSize
        format = book.format
        description = book.description
        fahasaLink = book.fahasaLink
        f.writerow([
            no,
            titleOriginal,
            title,
            isbn_10,
            isbn_13,
            titleLowerCase,
            titleNoMark,
            titleTail,
            description,
            authorName,
            authorNomark,
            # authorLink,
            translator,
            publisher,
            publishDate,
            imgLink,
            fahasaLink,
            # manufacturer,
            numOfPages,
            # bookSize,
            format,
            "",
            language,
            category
        ])

    def writeFileBookBasic(self, filename, no, bookBasic):
        f = csv.writer(open(filename, 'a', encoding="utf-8", newline=''))
        nameBook = bookBasic.nameBook,
        supplier = bookBasic.supplier
        authorName = bookBasic.authorName,
        publisher = bookBasic.publisher,
        publishDate = bookBasic.publishDate,
        description = bookBasic.description,
        category = bookBasic.category,
        language = bookBasic.language,
        pice = bookBasic.pice,
        imgLink = bookBasic.imgLink,
        fahasaLink = bookBasic.fahasaLink

        f.writerow([
            no,
            nameBook[0],
            authorName[0],
            supplier,
            publisher[0],
            publishDate[0],
            description[0],
            "",
            language[0],
            category[0],
            pice[0],
            imgLink[0],
            fahasaLink
        ])

    def writerTitle(self, filename):
        f = csv.writer(open(filename, 'w', newline=''))
        f.writerow(
            [
                "NO",
                "TitleOriginal",
                "Title",
                "isbn_10",
                "isbn_13",
                "TitleLowerCase",
                "TitleNoMark",
                "TitleTail",
                "Description",
                "AuthorName",
                "AuthorNameNoMark",
                # "authorLink",
                "Translator",
                "Publisher",  # issuer
                "PublishDate",
                "ImgLink",
                "FahasaLink",
                # "manufacturer",
                "NumOfPages",
                # "bookSize",
                "Format",
                "OrginalLanguage",
                "EditionLanguage",
                "Category",
            ])

    def writerTitleBasic(self, filename):
        f = csv.writer(open(filename, 'w', encoding="utf-8", newline=''))
        f.writerow(
            [
                "NO",
                "Tên sách",
                "Tác giả",
                "Nhà Cung Cấp",
                "Nhà xuất bản",
                "Ngày phát hành",
                "Giới thiệu sách",
                "Tóm lược",
                "Ngôn ngữ",
                "Thể Loại",
                "Giá bìa",
                "Link ảnh",
                "Link sách"
            ])

    def readFile(self, filename):
        csvfile = open(filename, "r",encoding="utf-8")
        table = csv.reader(csvfile)
        reader = []
        for row in table:
            reader.append(row)
        return reader

    def rowTable(self, dataTable, string):
        result = next((self.cleanTitle(trTable.find('td').text)
                       for trTable in dataTable.findAll('tr')
                       if trTable.find('th', class_='label').text == string), None)
        return result

    def getLogging(self):
        LOG_FORMAT = "%(asctime)s [%(levelname)s]- %(message)s"
        logging.basicConfig(handlers=[logging.FileHandler('log_crawler.log', 'a', 'utf-8')],
                            level=logging.DEBUG,
                            format=LOG_FORMAT)
        logger = logging.getLogger()
        return logger

    def cleanTitle(self, title):
        # remove redundant space
        title = title.strip().replace('\n', ',')
        pattern = re.compile(u"  +")
        title = pattern.sub(u" ", title)
        # print(title)
        return title


class crawlerData(processor):

    def dataWeb(self, html_book, linkBook, nameBook,img):
        logger = processor().getLogging()
        try:
            tableInformation = html_book.find('div', class_='product-collateral').find('div',class_='product-tabs-content').find('tbody')
        except Exception as error :
            logger.error("P1:"+str(error))
            return -1
        originalTitle = nameBook
        authorName = processor().rowTable(tableInformation, 'Tác giả')
        publisher = processor().rowTable(tableInformation, 'NXB')
        translator = processor().rowTable(tableInformation, 'Người Dịch')
        numOfPages = processor().rowTable(tableInformation, 'Số trang')
        format = processor().rowTable(tableInformation, 'Hình thức')
        publishDate = processor().rowTable(tableInformation, 'Năm XB')
        supplier = processor().rowTable(tableInformation, 'Tên Nhà Cung Cấp')
        fahasa_link = linkBook
        imgLink = img
        description_contents = html_book.find('div', {'id': 'product_tabs_description_contents'}).find('div', {'id': 'desc_content'})
        full_description = description_contents.findAll('p')
        description = ''
        for text_p in full_description:
            description = str(description) + str(text_p.text) + '\n'

        result = cleanDisplayTitle(originalTitle)
        title = result[0].title()
        titleTail = result[1]
        titleLowerCase = cleanSearchTitle(title).lower()
        titleNoMark = unidecode(titleLowerCase)
        if authorName != None:
            authorName = authorName.title()
            authorNoMark = unidecode(authorName)
        else:
            authorNoMark =None

        book = Book(
            titleOriginal=originalTitle,
            title=title,
            titleLowerCase=titleLowerCase,
            titleNoMark=titleNoMark,
            titleTail=titleTail,
            authorName=authorName,
            authorNomark=authorNoMark,
            authorLink='',
            translator=translator,
            imgLink=imgLink,
            manufacturer='',
            publisher=publisher,
            isbn_10='',
            isbn_13='',
            numOfPages=numOfPages,
            publishDate=publishDate,
            bookSize='',
            format=format,
            description=description,
            fahasaLink=fahasa_link,
            supplier = supplier
        )
        return book

    def dataWebBasic(self,book,category,language,pice):
        bookResult = BookBasic(
            nameBook = book.titleOriginal,
            authorName = book.authorName,
            publisher = book.publisher,
            publishDate = book.publishDate,
            description = book.description,
            category = category,
            language = language,
            pice = pice,
            imgLink = book.imgLink,
            fahasaLink = book.fahasaLink,
            supplier = book.supplier
        )
        return bookResult