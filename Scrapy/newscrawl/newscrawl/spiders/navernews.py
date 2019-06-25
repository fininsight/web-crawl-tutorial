# -*- coding: utf-8 -*-
import re
import scrapy
from newscrawl.items import NewscrawlItem
from datetime import timedelta, date
from urllib import parse
import time
import random
from time import sleep

start_date = date(2014, 1, 1)
end_date = date(2014, 12, 31)
cnt_per_page = 10
keyword = "대한항공"

url_format = "https://search.naver.com/search.naver?where=news&query={1}&sm=tab_opt&sort=0&photo=0&field=0&reporter_article=&pd=3&docid=&mynews=0&refresh_start=0&related=0&start={0}"
date_format = "&ds={0}&de={0}&nso=so%3Ar%2Cp%3Afrom{1}to{1}%2Ca%3Aall"

class NavernewsSpider(scrapy.Spider):
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    name = 'navernews'
    allowed_domains = ['naver.com','sedaily.com','khan.co.kr','einfomax.co.kr','joins.com','enewstoday.co.kr','view.asiae.co.kr','yna.co.kr', 'hankyung.com','news.mtn.co.kr','star.mbn.co.kr','weekly.donga.com','koreatimes.com','news.kbs.co.kr','cnbc.sbs.co.kr', 'hani.co.kr', 'mk.co.kr', 'etnews.com'] 
    start_urls = []

    for single_date in daterange(start_date, end_date):
        date_str = date_format.format(single_date.strftime("%Y.%m.%d"), single_date.strftime("%Y%m%d"))
        start_urls.append(url_format.format(1, keyword)+date_str)

    def parse(self, response):
        for href in response.xpath("//ul[@class='type01']/li/dl/dt/a/@href").extract() :
            yield response.follow(href, self.parse_details)
        
        total_cnt = int(re.sub('[()전체건,]', '', response.xpath("//div[@class='section_head']/div[1]/span/text()").get().split('/')[1]))
        query_str = parse.parse_qs(parse.urlsplit(response.url).query)
        currpage = int(query_str['start'][0]) 

        startdate = query_str['ds'][0]
        startdate2 = query_str['ds'][0].replace('.','')
        print("=================== [" + startdate + '] ' + str(currpage) + '/' + str(total_cnt) + "===================") 
        if currpage  < total_cnt : 
            yield response.follow(url_format.format(currpage+10, keyword) + date_format.format(startdate, startdate2)  , self.parse)

    def parse_details(self, response):            
        item = NewscrawlItem()
        item['url'] = response.url
        content = ""

        if 'sedaily.com' in response.url :
            item['title'] = response.xpath("//div[@id='v-left-scroll-in']/h2/text()").get()
            item['author'] = response.xpath("//div[@class='view_top']//li[1]/text()").get()
            item['date'] = response.xpath("//div[@class='view_top']//li[2]/text()").get().replace('승인 ','')
            content = str(response.xpath("//div[@itemprop='articleBody']").extract())

        if 'khan.co.kr' in response.url :
            item['title'] = response.xpath("//h1[@id='articleTtitle']/text()").get()
            item['author'] = response.xpath("//span[@class='name']/a/text()").get()
            item['date'] = response.xpath("//div[@class='pagecontrol']/div/em/text()").get().replace('입력 : ','')
            content = str(response.xpath("//div[@class='art_body']").extract())

        if 'news.joins.com' in response.url :
            item['title'] = response.xpath("//h1/text()").get()
            #item['author'] = response.xpath("//div[@id='head-info']//li[@class='name']/text()").get()
            item['date'] = response.xpath("//div[@class='byline']/em[2]/text()").get().replace('입력 ','')
            content = str(response.xpath("//div[@id='article_body']").extract())

        if 'einfomax.co.kr' in response.url :
            item['title'] = response.xpath("//div[@class='article-head-title']/text()").get()
            item['author'] = response.xpath("//div[@class='info-text']//li[1]/text()").get()
            item['date'] = response.xpath("//div[@class='info-text']//li[2]/text()").get().replace('승인 ','')
            content = str(response.xpath("//article[1]").extract())

        if 'enewstoday.co.kr' in response.url :
            item['title'] = response.xpath("//font[@class='headline-title']/text()").get()
            item['author'] = response.xpath("//div[@id='head-info']//li[@class='name']/text()").get()
            item['date'] = response.xpath("//div[@id='head-info']//li[@class='date']/text()").get().replace('승인 ','')
            content = str(response.xpath("//div[@id='articleBody']").extract())

        if 'view.asiae.co.kr' in response.url :
            item['title'] = response.xpath("//div[@class='area_title']/h3/text()").get().replace('\t','')
            item['author'] = response.xpath("//div[@class='e_article']/text()").get()
            item['date'] = response.xpath("//p[@class='user_data']/text()").get().split('>')[-1].strip()
            content = str(response.xpath("//div[@itemprop='articleBody']").extract())  

        if 'sports.news.naver.com' in response.url :
            item['title'] = response.xpath("//h4[@class='title']/text()").get().replace('\t','')
            #item['author'] = response.xpath("//div[@class='info']/span[1]/text()").get().replace('기사입력 ','')
            item['date'] = response.xpath("//div[@class='info']/span[1]/text()").get().replace('기사입력 ','')
            content = str(response.xpath("//div[@class='naver_post']").extract())     

        if 'yna.co.kr' in response.url :
            item['title'] = response.xpath("//h1[@class='tit-article']/text()").get().replace('\t','')
            #item['author'] = response.xpath("//div[@class='info']/span[1]/text()").get().replace('기사입력 ','')
            item['date'] = response.xpath("//div[@class='share-info']/span/em/text()").get().replace('기사입력 ','')
            content = str(response.xpath("//div[@class='article']").extract())  

        if 'hankyung.com' in response.url :
            item['title'] = response.xpath("//h1[@class='title']/text()").get().replace('\t','')
            #item['author'] = response.xpath("//div[@class='info']/span[1]/text()").get().replace('기사입력 ','')
            item['date'] = response.xpath("//span[@class='num']/text()").get().replace('기사입력 ','')
            content = str(response.xpath("//div[@id='articletxt']").extract())  

        if 'news.mtn.co.kr' in response.url :
            item['title'] = response.xpath("//h4/text()").get().replace('\t','')
            item['author'] = response.xpath("//span[@class='newsName']/text()").get()
            item['date'] = response.xpath("//span[@class='newsDate']/text()").get().replace('기사입력 ','')
            content = str(response.xpath("//div[@id='newsContent']").extract()) 

        if 'star.mbn.co.kr' in response.url :
            item['title'] = response.xpath("//h2/text()").get().replace('\t','')
            #item['author'] = response.xpath("//span[@class='newsName']/text()").get()
            item['date'] = response.xpath("//span[@class='sm_num']/text()").get().replace('기사입력 ','')
            content = str(response.xpath("//div[@id='artText']").extract())    

        if 'weekly.donga.com' in response.url :
            item['title'] = response.xpath("//div[@class='title']/h2/text()").get().replace('\t','')
            #item['author'] = response.xpath("//span[@class='newsName']/text()").get()
            item['date'] = response.xpath("//dl[@class='ver']/dd/text()").get().replace('기사입력 ','')
            content = str(response.xpath("//div[@itemprop='articleBody']").extract())   

        if 'koreatimes.com' in response.url :
            item['title'] = response.xpath("//div[@id='tit_arti']/h4/text()").get().replace('\t','')
            #item['author'] = response.xpath("//span[@class='newsName']/text()").get()
            item['date'] = response.xpath("//span[@class='upload_date']/text()").get().replace('기사입력 ','')
            content = str(response.xpath("//div[@id='print_arti']").extract())     

        if 'news.kbs.co.kr' in response.url :
            item['title'] = response.xpath("//div[@class='landing-caption']/h5/text()").get().replace('\t','')
            #item['author'] = response.xpath("//span[@class='newsName']/text()").get()
            item['date'] = response.xpath("//div[@class='landing-caption']/span[@class='txt-info']/em[1]/text()").get().replace('기사입력 ','')
            content = str(response.xpath("//div[@id='cont_newstext']").extract())  

        if 'cnbc.sbs.co.kr' in response.url :
            item['title'] = response.xpath("//h3[@class='ah_big_title']/text()").get()
            item['author'] = response.xpath("//span[@class='ahi_name']/text()").get()
            item['date'] = response.xpath("//span[@class='ahi_date']/text()").get().replace('입력 ','')
            content = str(response.xpath("//div[@class='article_body']").extract())     

        if 'hani.co.kr' in response.url :
            item['title'] = response.xpath("//span[@class='title']/text()").get()
            #item['author'] = response.xpath("//span[@class='ahi_name']/text()").get()
            item['date'] = response.xpath("//p[@class='date-time']/span[1]/text()").get().replace('입력 ','')
            content = str(response.xpath("//div[@itemprop='articleBody']").extract())   

        if 'mk.co.kr' in response.url :
            item['title'] = response.xpath("//h1[@class='top_title']/text()").get()
            item['author'] = response.xpath("//li[@class='author']/text()").get()
            item['date'] = response.xpath("//li[@class='lasttime']/text()").get().replace('입력 ','')
            content = str(response.xpath("//div[@itemprop='articleBody']").extract()) 

        if 'etnews.com' in response.url :
            item['title'] = response.xpath("//h2[@class='article_title']/text()").get()
            #item['author'] = response.xpath("//li[@class='author']/text()").get()
            item['date'] = response.xpath("//time[@class='date']/text()").get().replace('발행일 : ','')
            content = str(response.xpath("//div[@itemprop='articleBody']").extract())  

        content = re.sub('<[^>]*>', '', content)
        content = content.replace('\\r','').replace('\\n','').replace('\\t','').replace('  ','').strip()
        item['content'] = content       

        yield item

