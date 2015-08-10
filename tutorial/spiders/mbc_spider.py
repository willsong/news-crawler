# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import MbcArticleItem
import MySQLdb

class MbcSpider(scrapy.Spider):
    name = 'Mbc'
    allowed_domains = ['imbc.com']
    start_urls = []

    s_date = ''
    page_cnt = 1
    dont_filter = False

    '''
    Constructor
    '''
    def __init__(self, search_date = '2015-08-01', *args, **kwargs):
        self.s_date = search_date
        self.start_urls = [self.get_query_url(self.s_date)]
        print self.start_urls

    '''
    Get the query url
    '''
    def get_query_url(self, search_date):
        #qs = {'query': keyword}

        return 'http://imnews.imbc.com/player/list_frame.aspx?ntype=vod&category=desk' \
                + '&day=' + search_date.replace("-","")

    '''
    Starting point.
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def parse(self, response):

        try:
        
            news_list = response.xpath('//div[@class="list"]/ul/li')
            
            for news_article in news_list:
                #get news id 
                #print news_article.extract()
                news_id =  news_article.xpath("./p/a/@onclick").extract()
                news_id = news_id[0].split("'")[1]
                news_url = "http://imnews.imbc.com/replay/2015/nwdesk/article/"+news_id+"_14775.html"
                
                #news_title  = news_article.xpath('./p/a//text()').extract()
                #print news_title[0]
                #news_reporter = news_article.xpath('./span[@class = "j_list"]/text()').extract()
                
                article = MbcArticleItem()
                article['url'] = news_url
                article['aid'] = news_id
                
                req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)
                
                req.meta['article'] = article
                yield req
        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!  URL :'+ news_reporter[0]
            print traceback.print_exc(file = sys.stdout)

        
    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''
    def parse_news(self, response):

        # populate the rest of the article
        article = response.meta['article']

        title =  response.xpath('//div[@class="news-view"]//p[@class="view-title"]/text()').extract()
        #print title[0]
        datetime = response.xpath('//div[@class="news-view"]//p[@class="article-time"]/span[@class="article-time-date"]/text()').extract()
        #print datetime
        reporter = response.xpath('//div[@class="news-view"]//p[@class="article-time"]/span[@class="reporter"]/text()').extract()
        #print reporter[0]
        content = response.xpath('//div[@class="news-view"]//div[@class="view-con"]//text()').extract()
        #print content
        
        new_time = time.strptime(datetime[0], "%Y-%m-%d %H:%M")  
        
        article['title'] = title[0]
        article['date'] = time.strftime('%Y-%m-%d %H:%M:00', new_time)
        article['contents'] = ''.join(content)
        article['reporter'] = reporter[0] if len(reporter)>0 else '' 
        #print article
        
        #yield article
