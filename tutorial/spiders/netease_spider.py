# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import NeteaseArticleItem
import MySQLdb

class NeteaseSpider(scrapy.Spider):
    name = '163'
    allowed_domains = ['163.com']
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

        #return 'http://imnews.imbc.com/player/list_frame.aspx?ntype=vod&category=desk' \
        #        + '&day=' + search_date.replace("-","")
        return 'http://news.163.com/special/0001220O/news_json.js'

    '''
    Starting point.
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def GetMiddleStr(self,content,startStr,endStr):
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
        endIndex = content.index(endStr)
        return content[startIndex: endIndex]
    def parse(self, response):

        try:
            #Get news.163.com's json data
            response = urllib2.urlopen(r'http://news.163.com/special/0001220O/news_json.js')
            html_gbk = response.read()

            # gbk-->utf8
            html_utf = html_gbk.decode("gbk").encode("utf-8")

            # transfer to std json format
            js = self.GetMiddleStr(html_utf,'var data={"category":','],[]]};')
            js_0 = js.replace('[','')
            js_1 = js_0.replace(']','')
            js_2 = js_1.replace('"news":','')
            news_json ='[' + js_2 + ']'

            # 'c':category  't':news title  'l':url  'p':time
            hjson = json.loads(news_json, encoding ="utf-8")
            print 'news size is :' +str(len(hjson))
            count = 0
            for items in hjson:
                count +=1
                #if count>200: break
                if count<9: continue
                #print items
                for (k, v) in items.items():
                    if k == 'p': news_time = v
                #news_url = 'http://news.163.com/15/0815/19/B134PU1E000146BE.html'
                news_url = items['l']
                
                article = NeteaseArticleItem()
                article['url'] = news_url
                article['date'] = news_time
                req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)
                
                req.meta['article'] = article
                yield req
        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!  URL :'
            print traceback.print_exc(file = sys.stdout)

        
    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''
    def parse_news(self, response):
        try:
            # populate the rest of the article
            article = response.meta['article']
            aid = str(article['url'])[article['url'].rfind('/')+1:-5]
            title =  response.xpath('//div[@class="ep-content"]//h1[@id="h1title"]/text()').extract()
            #print title
            
            agency = response.xpath('//div[@class="ep-content"]//a[@id="ne_article_source"]/text()').extract()
            #print agency
            
            content = response.xpath('//div[@class="ep-content"]//div[@id="endText"]/p/text()').extract()
            
            article['title'] = title[0]
            article['agency'] = agency[0]
            article['aid'] = aid
            article['contents'] = ''.join(content)
             
            #print article
            
            yield article
        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!  URL :'+ article['url']
            print traceback.print_exc(file = sys.stdout)
