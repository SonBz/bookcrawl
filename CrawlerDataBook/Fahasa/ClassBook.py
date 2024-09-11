class Book:
    def __init__(self, titleOriginal,title,titleLowerCase,titleNoMark,titleTail,authorName,authorNomark,authorLink,translator,imgLink,manufacturer,
                publisher,isbn_10,isbn_13,numOfPages,publishDate,bookSize,format,description,fahasaLink,supplier):

        self.title = title
        self.titleOriginal = titleOriginal
        self.titleLowerCase = titleLowerCase
        self.titleNoMark = titleNoMark
        self.titleTail = titleTail
        self.authorName = authorName
        self.authorNomark = authorNomark
        self.authorLink = authorLink
        self.translator = translator
        self.imgLink = imgLink
        self.manufacturer = manufacturer
        self.publisher = publisher
        self.isbn_10 = isbn_10
        self.isbn_13 = isbn_13
        self.numOfPages = numOfPages
        self.publishDate = publishDate
        self.bookSize = bookSize
        self.format = format
        self.description = description
        self.fahasaLink = fahasaLink
        self.supplier = supplier

# Tên sách,Tên tác giả,Ngôn ngữ,Chủ đề,Nhà xuất bản,Ngày phát hành,Giá bìa,Tóm lược, giới thiệu sách
class BookBasic:
    def __init__(self,nameBook,authorName,publisher,publishDate,description,category,language,pice,imgLink,fahasaLink,supplier):
        self.nameBook = nameBook
        self.authorName = authorName
        self.publisher = publisher
        self.publishDate = publishDate
        self.description = description
        self.category = category
        self.language = language
        self.pice = pice
        self.imgLink = imgLink
        self.fahasaLink = fahasaLink
        self.supplier = supplier

#