# coding=utf-8
import csv
import re

def cleanDisplayTitle(title):
     #trim title
    title = title.strip().lower()
    listOfSub = ""
    pattern = re.compile(u"[\t\n\r\f\v]")
    title = pattern.sub(u" ", title)
    #remove redundant space
    pattern = re.compile(u"  +")
    title = pattern.sub(u" ", title)
    #Search Tập/Phần....
    chapters = [u"phần [0-9i]+", u"tập [0-9]+", u"chapter [0-9]+"]
    for chapter in chapters:
        pattern = re.compile(chapter)
        match = pattern.search(title)
        if match:
            title = title[:match.start()] + title[match.end():] + " " + title[match.start(): match.end()]
    #get all pattern like (....)
    while True:
        startIdx = title.find(u"(")
        if (startIdx < 0):
            break
        endIdx = title.find(u")", startIdx)
        if (endIdx < 0):
            break
        if listOfSub == "":
            listOfSub += title[startIdx+1: endIdx].strip()
        else:
            listOfSub += u";"
            listOfSub += title[startIdx+1: endIdx].strip()
        result = ""
        if (startIdx > 0):
            result = title[:startIdx-1]
        if (endIdx < len(title)-1):
            result += title[endIdx+1:]
        title = result
    chapters = [u"trọn bộ [0-9]+ tập",
                u"trọn bộ [0-9]+ phần",
                u"tái bản [0-9]+",
                u"tái bản lần thứ [0-9]+",
                u"phiên bản .*",
                u"bìa cứng",
                u"bìa mềm"
                ]
    for chapter in chapters:
        pattern = re.compile(chapter)
        match = pattern.search(title)
        if match:
            if listOfSub == "":
                listOfSub += title[match.start(): match.end()].strip()
            else:
                listOfSub += ";"
                listOfSub += title[match.start(): match.end()].strip()
            title = title[:match.start()] + title[match.end():]
    #replace all
    pattern = re.compile(u"[\"`':?;,&%$#!()~^|*\[\]\{\}\-\.]+$")
    title = pattern.sub("", title)
    pattern = re.compile(u"- -")
    title = pattern.sub(u"-", title)
    title = title.strip()
    #remove redundant space
    pattern = re.compile(u"  +")
    title = pattern.sub(u" ", title)
    #print(title)
    #print(listOfSub)
    return (title, listOfSub)
def cleanSearchTitle(title):
    #replace all :
    pattern = re.compile(u"[\"`':?;,&%$#!()~^|*\[\]\{\}\-\.]")
    title = pattern.sub(u" ", title)
     #remove redundant space
    title = title.strip()
    pattern = re.compile(u"  +")
    title = pattern.sub(u" ", title)
    #print(title)
    return title