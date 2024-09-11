# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, Compose, MapCompose, TakeFirst, Join
from dateutil.parser import parse as dateutil_parse
from w3lib.html import remove_tags
import re
from unidecode import unidecode

BOOK_TYPE = "book"
AUTHOR_TYPE = "author"
PPDVN_TYPE = "ppdvn"

def num_page_extractor(num_pages):
    if num_pages:
        return num_pages.split()[0]
    return None

def filter_empty(vals):
    return [v.strip() for v in vals if v.strip()]


def split_by_newline(txt):
    return txt.split("\n")

def safe_parse_date(date):
    try:
        date_time = dateutil_parse(date, fuzzy=True).strftime("%Y/%m/%d")
    except ValueError:
        date_time = "None"

    return date_time

def extract_publish_dates(maybe_dates):
    maybe_dates = [s for s in maybe_dates if "published" in s.lower()]
    return [safe_parse_date(date) for date in maybe_dates]


def extract_year(s):
    s = s.lower().strip()
    match = re.match(".*first published.*(\d{4})", s)
    if match:
        return match.group(1)


def extract_ratings(txt):
    """Extract the rating histogram from embedded Javascript code

        The embedded code looks like this:

        |----------------------------------------------------------|
        | renderRatingGraph([6, 3, 2, 2, 1]);                      |
        | if ($('rating_details')) {                               |
        |   $('rating_details').insert({top: $('rating_graph')})   |
        |  }                                                       |
        |----------------------------------------------------------|
    """
    codelines = "".join(txt).split(";")
    rating_code = [line.strip() for line in codelines if "renderRatingGraph" in line]
    if not rating_code:
        return None
    rating_code = rating_code[0]
    rating_array = rating_code[rating_code.index("[") + 1 : rating_code.index("]")]
    ratings = {5 - i:int(x) for i, x in enumerate(rating_array.split(","))}
    return ratings

def split_by_commma(txt):
    # print(txt)
    return txt.split(",")

def clean_space(txt):
    txt = re.sub(r'[\t\n\r\f\v]', r'', txt)
    txt = re.sub(r' {2}', r' ', txt)
    return txt

def clean_hyphen(txt):
    return ''.join(txt.split('-'))


def clean_test(txt):
    nstr = re.sub(r'[,|;|]', r',', txt)
    if ',' in nstr:
        yield nstr.split(',')
    yield txt

def string_domain(txt):
    return 'www.nxbkimdong.com.vn'+txt

def release_date(string_date):
    nstr = re.sub(r'[/|-]', '/', string_date)
    split_str = nstr.split('/')
    if len(split_str) == 2:
        string_two = [split_str[1], split_str[0]]
        yield '/'.join(string_two)
    else:
        string_two = [split_str[2], split_str[1], split_str[0]]
        yield '/'.join(string_two)

def publisher_extractor(txt):
    if txt:
        if 'by' in txt:
            publisher = txt.split('by')[-1]
            nstr = re.sub(r'[||&]', '&', publisher)
            return nstr.split('&')
        return None
    else:
        return None

class BookcrawlerItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BookItem(Item):
    item_type = BOOK_TYPE

    name = Field(input_processor=MapCompose(str.strip, clean_space))
    name_unidecode = Field(input_processor=MapCompose(str.strip, clean_space))
    author = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma), output_processor=Compose(list))
    description = Field(input_processor=MapCompose(str.strip))
    price = Field(input_processor=MapCompose(str.strip, clean_space))
    image_uri = Field(input_processor=MapCompose(str.strip))

    # Information fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

class AuthorItem(Item):
    item_type = AUTHOR_TYPE
    # Scalars
    url = Field()

    name = Field(input_processor=MapCompose(str.strip, clean_space))
    name_unidecode = Field(input_processor=MapCompose(str.strip, clean_space))
    birth_date = Field(input_processor=MapCompose(safe_parse_date, clean_space))
    death_date = Field(input_processor=MapCompose(safe_parse_date, clean_space))
    born= Field(input_processor=MapCompose(clean_space))

    avg_rating = Field(serializer=float)
    num_ratings = Field(serializer=int)
    num_reviews = Field(serializer=int)

    # Lists
    genres = Field(output_processor=Compose(set, list))
    influences = Field(output_processor=Compose(set, list))

    # Blobs
    about = Field(
        # Take the first match, remove HTML tags, convert to list of lines, remove empty lines, remove the "edit data" prefix
        input_processor=Compose(TakeFirst(), remove_tags, split_by_newline, filter_empty, lambda s: s[1:]),
        output_processor=Join()
    )

    img_url=Field(input_processor=MapCompose(str.strip))
    
    # Information fields
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

class GoodreadsBookItem(Item):
    item_type = BOOK_TYPE

    name = Field(input_processor=MapCompose(str.strip, clean_space))
    name_unidecode = Field(input_processor=MapCompose(str.strip, clean_space))
    author = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma), output_processor=Compose(list))
    author_unidecode = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma), output_processor=Compose(list))
    author_url = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma), output_processor=Compose(list))
    description = Field(input_processor=MapCompose(str.strip))
    price = Field(input_processor=MapCompose(str.strip, clean_space))
    image_uri = Field(input_processor=MapCompose(str.strip))
    num_ratings = Field(input_processor=MapCompose(str.strip, clean_space))
    num_reviews = Field(input_processor=MapCompose(str.strip, clean_space))
    avg_rating = Field(input_processor=MapCompose(str.strip, clean_space))
    num_pages = Field(input_processor=MapCompose(str.strip, clean_space, num_page_extractor))
    language = Field(input_processor=MapCompose(str.strip, clean_space))
    publish_date = Field(input_processor=MapCompose(extract_publish_dates, clean_space))

    original_publish_year = Field(input_processor=MapCompose(extract_year, clean_space))

    isbn = Field(input_processor=MapCompose(str.strip, clean_space))
    series = Field(input_processor=MapCompose(str.strip, clean_space))

    # Lists
    awards = Field(input_processor=MapCompose(str.strip, clean_space))
    places = Field(input_processor=MapCompose(str.strip, clean_space))
    characters = Field(input_processor=MapCompose(str.strip, clean_space))
    genres = Field(output_processor=Compose(set, list))

    img_url=Field(input_processor=MapCompose(str.strip))
    publisher_name = Field(input_processor=MapCompose(str.strip,clean_space,publisher_extractor),
                           output_processor=Compose(list))

    # Dicts
    # rating_histogram = Field(input_processor=MapCompose(extract_ratings))

    # Information fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

class KimDongBookItem(Item):
    item_type = BOOK_TYPE

    name = Field(input_processor=MapCompose(str.strip, clean_space))
    name_unidecode = Field(input_processor=MapCompose(str.strip, clean_space))
    author = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma), output_processor=Compose(list))
    author_unidecode = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma), output_processor=Compose(list))
    author_url = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma),output_processor=Compose(list))
    description = Field(input_processor=MapCompose(str.strip))
    price = Field(input_processor=MapCompose(str.strip, clean_space))
    image_uri = Field(input_processor=MapCompose(str.strip))
    num_pages = Field(input_processor=MapCompose(str.strip, clean_space, num_page_extractor))
    publish_date = Field(input_processor=MapCompose(clean_space, release_date))
    isbn = Field(input_processor=MapCompose(str.strip, clean_space,clean_hyphen))
    series = Field(input_processor=MapCompose(str.strip, clean_space))

    # books = Field(input_processor=MapCompose(str.strip, clean_space))
    # books_url = Field(input_processor=MapCompose(str.strip, clean_space, string_domain))
    weight = Field(input_processor=MapCompose(str.strip, clean_space))
    format = Field(input_processor=MapCompose(str.strip, clean_space))

    # Information fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

class PPDVNPublishedItem(Item):
    item_type = PPDVN_TYPE

    name = Field(input_processor=MapCompose(str.strip, clean_space))
    name_unidecode = Field(input_processor=MapCompose(str.strip, clean_space, unidecode))
    author = Field(input_processor=MapCompose(str.strip, clean_space))
    author_unidecode = Field(input_processor=MapCompose(str.strip, clean_space, unidecode))

    isbn = Field(input_processor=MapCompose(str.strip, clean_space, clean_hyphen))
    editors = Field(input_processor=MapCompose(str.strip, clean_space))
    editors_unidecode = Field(input_processor=MapCompose(str.strip, clean_space, unidecode))
    publisher_name = Field(input_processor=MapCompose(str.strip, clean_space))
    associate_partner = Field(input_processor=MapCompose(str.strip, clean_space))
    print_location = Field(input_processor=MapCompose(str.strip, clean_space))
    date_lc = Field(input_processor=MapCompose(release_date))
    status = Field(seralizer=int)

    # Information fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

class PPDVNNotPublishedItem(Item):
    item_type = PPDVN_TYPE

    name = Field(input_processor=MapCompose(str.strip, clean_space))
    name_unidecode = Field(input_processor=MapCompose(str.strip, clean_space, unidecode))
    author = Field(input_processor=MapCompose(str.strip, clean_space))
    author_unidecode = Field(input_processor=MapCompose(str.strip, clean_space, unidecode))

    isbn = Field(input_processor=MapCompose(str.strip, clean_space, clean_hyphen))
    translators = Field(input_processor=MapCompose(str.strip, clean_space))
    registration_number = Field(input_processor=MapCompose(str.strip, clean_space))
    associate_partner = Field(input_processor=MapCompose(str.strip, clean_space))
    number_of_print = Field(input_processor=MapCompose(str.strip, clean_space))
    self_publish = Field(seralizer=int)
    status = Field(seralizer=int)

    # Information fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

class TikiBookItem(Item):
    item_type = BOOK_TYPE

    name = Field(input_processor=MapCompose(str.strip, clean_space))
    name_unidecode = Field(input_processor=MapCompose(str.strip, clean_space))
    author = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma), output_processor=Compose(list))
    author_unidecode = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma),
                             output_processor=Compose(list))
    author_url = Field(input_processor=MapCompose(str.strip, clean_space, split_by_commma),output_processor=Compose(list))
    description = Field(input_processor=MapCompose(str.strip))
    price = Field(input_processor=MapCompose(str.strip, clean_space))
    avg_rating = Field(serializer=float)
    num_ratings = Field(serializer=int)
    num_pages = Field(input_processor=MapCompose(str.strip, clean_space, num_page_extractor))
    publish_date = Field(input_processor=MapCompose(str.strip, clean_space, release_date))
    isbn = Field(input_processor=MapCompose(str.strip, clean_space))
    format = Field(input_processor=MapCompose(str.strip, clean_space))
    img_url = Field(input_processor=MapCompose(str.strip))
    publisher_name = Field(input_processor=MapCompose(str.strip, clean_space))
    dimensions = Field(input_processor=MapCompose(str.strip, clean_space))
    manufacturer = Field(input_processor=MapCompose(str.strip, clean_space))
    sku = Field(input_processor=MapCompose(str.strip, clean_space))
    translators = Field(input_processor=MapCompose(str.strip, clean_space))

    # Information fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

class AuthorLoader(ItemLoader):
    default_output_processor = TakeFirst()

class BookLoader(ItemLoader):
    default_output_processor = TakeFirst()

class PPDVNLoader(ItemLoader):
    default_output_processor = TakeFirst()