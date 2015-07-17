# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NaverArticleItem(scrapy.Item):
    aid = scrapy.Field()
    oid = scrapy.Field()
    date = scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    referer = scrapy.Field()

class NaverCommentItem(scrapy.Item):
    date = scrapy.Field()
    aid = scrapy.Field()
    username = scrapy.Field()
    like_count = scrapy.Field()
    dislike_count = scrapy.Field()
    contents = scrapy.Field()
