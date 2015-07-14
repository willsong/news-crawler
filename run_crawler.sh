#!/bin/bash

scrapy crawl Naver -a start_date='2015-05-10' -a end_date='2015-05-20' &> tutorial/spiders/logs/log0510-0520.txt
scrapy crawl Naver -a start_date='2015-05-21' -a end_date='2015-05-31' &> tutorial/spiders/logs/log0521-0531.txt
scrapy crawl Naver -a start_date='2015-06-01' -a end_date='2015-06-10' &> tutorial/spiders/logs/log0601-0610.txt
scrapy crawl Naver -a start_date='2015-06-11' -a end_date='2015-06-20' &> tutorial/spiders/logs/log0611-0620.txt
scrapy crawl Naver -a start_date='2015-06-21' -a end_date='2015-06-30' &> tutorial/spiders/logs/log0621-0630.txt
scrapy crawl Naver -a start_date='2015-07-01' -a end_date='2015-07-10' &> tutorial/spiders/logs/log0701-0710.txt
scrapy crawl Naver -a start_date='2015-07-11' -a end_date='2015-07-14' &> tutorial/spiders/logs/log0711-0714.txt
