# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import NaverArticleItem, NaverCommentItem
import MySQLdb

class NaverSpider(scrapy.Spider):
    name = 'Naver'
    allowed_domains = ['naver.com']
    start_urls = []

    s_date = ''
    e_date = ''
    page_cnt = 1
    dont_filter = False

    '''
    Constructor
    '''
    def __init__(self, start_date = '', end_date = '',check_date = '', *args, **kwargs):
        self.s_date = start_date
        self.e_date = end_date
        self.c_date = check_date
        self.start_urls = [self.get_query_url(self.s_date, self.e_date, self.page_cnt)]
        super(NaverSpider, self).__init__(*args, **kwargs)

    '''
    Get the query url
    '''
    def get_query_url(self, start_date, end_date, page):
        #qs = {'query': keyword}

        return 'http://news.naver.com/main/search/search.nhn' \
                + '?query=%B0%A1' \
                + '&startDate=' + start_date \
                + '&endDate=' + end_date \
                + '&page=' + str(page) \
                + '&newscode=032' \
                + '&newscode=020' \
                + '&newscode=023' \
                + '&newscode=025' \
                + '&newscode=028' \
                + '&rcnews=exist:032:020:023:025:028:'


    def geturl_by_day(self):

        try:
            conn = MySQLdb.connect(
                    host = 'localhost',
                    user = 'mers_zhwang',
                    passwd = 'Khhd7ALtc8XLhwVK',
                    charset = 'utf8'
                    )
            cur = conn.cursor()
            conn.select_db('mers_zhwang')
            #sql = "select url from articles where date like '%%" + self.c_date + "%%'"
            sql = "select url from articles where date(date) = '" + self.c_date + "'"
            url = cur.execute(sql)
            print '%s records' % url
            urllist = cur.fetchall()
            cur.close()
            conn.close()
            return urllist
        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' % (e.args[0], e.args[1])

    def parse_day(self):
        url_lists = self.geturl_by_day()
        for url in url_lists:
            print '=========================================' + url[0]
            url_code = urllib.urlopen(url[0]).getcode()
            print '==============: ', url_code
            st_urlcode = '%d' % url_code
            #http code: 1xx,2xx,3xx,4xx,5xx, where only 2xx indicates success
            if st_urlcode.startswith ('4'):
                self.update_deleted(url[0])
            elif st_urlcode.startswith('3'):
               self.update_deleted(url[0])
            elif st_urlcode.startswith('1'):
               self.update_deleted(url[0])
            elif st_urlcode.startswith('5'):
               self.update_deleted(url[0])
    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def parse(self, response):

        '''
        if len(self.c_date) >0 :
            self.parse_day()
            return
        '''
        self.parse_day()

        # determine whether to go ahead with parse or not
        result_header = response.css('div.result_header > span.result_num').xpath('.//text()').extract()[0].strip()
        res = re.match(u'^\((\d+).*?(\d+).*?\)$', result_header, re.M|re.S)

        start_rec = int(res.group(1))
        total_rec = int(res.group(2))

        print 'Record %s of %s' % (start_rec, total_rec)

        if start_rec < total_rec:

            print 'Page %s' % self.page_cnt

            cnt = 0
            for news_article in response.css('ul.srch_lst > li > div.ct'):
                try:
                    # news agency
                    agency = news_article.css('div.info > span.press').xpath('.//text()').extract()[0]

                    # naver news link
                    news_url = news_article.css('div.info > a.go_naver::attr("href")').extract()[0]

                    # parse news link to get aid and oid
                    parsed_news_url = urlparse(news_url)
                    host_part = parsed_news_url[1]
                    query_string = parse_qs(parsed_news_url[4])

                    # populate article item
                    if host_part == 'sports.news.naver.com':
                        article = NaverArticleItem()
                        article['oid'] = query_string['office_id'][0]
                        article['aid'] = query_string['article_id'][0]
                        article['agency'] = agency
                    else:
                        article = NaverArticleItem()
                        article['aid'] = query_string['aid'][0]
                        article['oid'] = query_string['oid'][0]
                        article['agency'] = agency

                        # sometimes the news URL is m.news.naver.com
                        # change it to the normal news.naver.com URL
                        if host_part == 'm.news.naver.com':
                            news_url = 'http://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1=102&oid=%s&aid=%s' % (article['oid'], article['aid'])

                    req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)

                    article['referer'] = response.url
                    req.meta['article'] = article
                    yield req
                    cnt += 1
                except Exception, e:
                    print 'ERROR!!!!!!!!!!!!!  URL :' + news_url
                    print traceback.print_exc(file = sys.stdout)
                    pass

            print 'read %s articles' % cnt
            self.update_count('articles', cnt)

            self.page_cnt += 1

            next_page_url = self.get_query_url(self.s_date, self.e_date, self.page_cnt)
            yield scrapy.Request(next_page_url, callback = self.parse, dont_filter = self.dont_filter)


    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''
    def parse_news(self, response):

        # populate the rest of the article
        article = response.meta['article']
        article['url'] = response.url

        title = ''
        date = ''

        parsed_response_url = urlparse(response.url)
        host_part = parsed_response_url[1]

        if host_part == 'entertain.naver.com':
            title = response.css('p.end_tit').xpath('.//text()').extract()[0]
            date = response.css('div.article_info > span.author > em').xpath('.//text()').extract()[0]
            date = time.strftime('%Y-%m-%d %H:%M:00', self.parse_date(date))
            contents = ' '.join(response.css('div#articeBody').xpath('.//text()').extract()).strip()
        elif host_part == 'sports.news.naver.com':
            title = response.css('div.articlehead > h4').xpath('.//text()').extract()[0]
            date = response.css('div.info_article > span.time').xpath('.//text()').extract()[0]
            contents = ' '.join(response.css('div.article > div').xpath('.//text()').extract()).strip()

        else:
            title = response.css('div.article_info > h3').xpath('.//text()').extract()[0]
            date = response.css('div.article_info > div.sponsor > span.t11').xpath('.//text()').extract()[0]
            contents = ' '.join(response.css('div#articleBodyContents').xpath('.//text()').extract()).strip()

        article['title'] = title
        article['contents'] = contents
        article['date'] = date

        # this is the hidden 'comment count' api used by naver
        comment_check_url = 'http://m.news.naver.com/api/comment/count.json'

        comment_count_data = {
            'gno' : 'news' + article['oid'] + ',' + article['aid']
        }

        req = scrapy.FormRequest(comment_check_url, formdata = comment_count_data, callback = self.parse_comment_count, dont_filter = self.dont_filter)
        req.meta['article'] = article

        return req

    '''
    Retrieve comment count for a given news article.
    Args:
     response - the response object pertaining to the json response of the comment count api call
    '''
    def parse_comment_count(self, response):
        json_response = json.loads(response.body)
        comment_count = int(json_response['message']['result']['count'])
        self.update_count('comments', comment_count)

        yield response.meta['article']
        self.update_count('ayield', 1)

        if comment_count > 0:

            # this is the hidden 'comment list' api used by naver
            comment_url = 'http://m.news.naver.com/api/comment/list.json'

            comment_data = {
                'gno' : 'news' + response.meta['article']['oid'] + ',' + response.meta['article']['aid'],
                'page': '1',
                'sort': 'newest',
                'pageSize': str(comment_count),
                'serviceId' : 'news'
            }

            req = scrapy.FormRequest(comment_url, formdata = comment_data, callback = self.parse_comments, dont_filter = self.dont_filter)
            req.meta['article'] = response.meta['article']
            yield req

    '''
    Retrieve the list of comments for a given news article
    Args:
     response - the response object pertaining to the json response of the comment list api call
    '''
    def parse_comments(self, response):
        json_response = json.loads(response.body)
        for comment in json_response['message']['result']['commentReplies']:

            new_time = self.parse_date(comment['sRegDate'])

            comment_item = NaverCommentItem()
            comment_item['date'] = time.strftime('%Y-%m-%d %H:%M:00', new_time)
            comment_item['aid'] = response.meta['article']['aid']
            comment_item['username'] = comment['userNickname']
            comment_item['like_count'] = comment['goodCount']
            comment_item['dislike_count'] = comment['badCount']
            comment_item['contents'] = comment['content']

            yield comment_item

    '''
    Parse a date string in the form of '2015.07.10 오후 2:39' and return a time object
    Args:
     orig_date_str - the origina string to parse
    Returns:
     python time object
    '''
    def parse_date(self, orig_date_str):

        # date is in the form of '2015.07.10 오후 2:39'
        # change to python time object
        regex_res = re.match(u'^(\d{4}\.\d{2}\.\d{2})(.*?)(\d{1,2}:\d{2})$', orig_date_str, re.M|re.S)

        am_or_pm = regex_res.group(2).strip()
        if am_or_pm == u'\uc624\uc804':
            am_or_pm = 'AM'
        elif am_or_pm == u'\uc624\ud6c4':
            am_or_pm = 'PM'

        new_time_str = '%s %s %s' % (
            regex_res.group(1),
            regex_res.group(3),
            am_or_pm
        )

        new_time = time.strptime(new_time_str, '%Y.%m.%d %I:%M %p')
        return new_time

    '''
    Debug method - update deleted column
    '''
    def update_deleted(self, url):

        try:
            conn = MySQLdb.connect(
                    host = 'localhost',
                    user = 'mers_zhwang',
                    passwd = 'Khhd7ALtc8XLhwVK',
                    charset = 'utf8'
                    )
            cur = conn.cursor()
            conn.select_db('mers_zhwang')

            sql = "update articles set deleted = 'Y' where url = '%s'" % (url)
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' % (e.args[0], e.args[1])


    '''
    Debug method - update the given count
    '''

    def update_count(self, tpe, cnt):
        try:
            conn = MySQLdb.connect(
                    host = 'localhost',
                    user = 'mers_zhwang',
                    passwd = 'Khhd7ALtc8XLhwVK',
                    charset = 'utf8'
                    )
            cur = conn.cursor()
            conn.select_db('mers_zhwang')

            sql = 'update counts set v = v + %s where k = "%s"' % (cnt, tpe)
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' % (e.args[0], e.args[1])

    '''
    Debug method - insert the given url
    '''

    def update_url(self, url):
        try:
            conn = MySQLdb.connect(
                    host = 'localhost',
                    user = 'mers_zhwang',
                    passwd = 'Khhd7ALtc8XLhwVK',
                    charset = 'utf8'
                    )
            cur = conn.cursor()
            conn.select_db('mers_zhwang')

            sql = 'insert into urls set url = "%s"' % url
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' % (e.args[0], e.args[1])

