#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
root_mod = '/home/xxguo/Project/crawler'
sys.path.append(root_mod)

reload(sys)
sys.setdefaultencoding('utf-8')
import re
import time
import random
from lxml import etree
from datetime import datetime
from urllib import quote, unquote
#from bs4 import BeautifulSoup
from scheduler.crawler import Crawler, export, Scheduler
from models.search.model import SearchArticleModel
from utils.readability import Readability
from crawlerimpl.zjld.processdata import HandleUrl , HandleContent, \
        get_urls_re, get_charset, clear_label, clear_space, new_time, \
        local2utc, get_code, clear_a


def _get_url(url, code='utf-8'):
    time.sleep(random.randint(0,3))
    html_stream = get_urls_re(url, time = 6)
    cod = get_code(url)
    try:
        if cod:
            html_stream.encoding = cod.get('encoding', code)
        else:
            html_stream.encoding = get_charset(html_stream.text)
        if html_stream.status_code != 200:
            return html_stream
    except:
        pass
    return html_stream

class EventCrawler(Crawler):

    type = "zjld.baidu.newstitle"

    @staticmethod
    def init(conf=None):

        from xlutils.copy import copy
        import xlrd
        import os
        SRC_PATH = os.path.dirname(__file__)
        bk = xlrd.open_workbook(os.path.join(SRC_PATH,
                                 "../../file/event.xls"))
        sh = bk.sheet_by_name('Sheet1')
        nrows = sh.nrows
        ncols = sh.ncols
        for i in xrange(1,nrows):

            source_type = sh.cell_value(i,1).strip()
            if source_type == '':
                continue
            data = {
                'source_type': source_type,
            }
            
            key = sh.cell_value(i,0).strip()
            Scheduler.schedule(EventCrawler.type ,key=str(key), 
                                data=data, interval=7200, reset=True)
            weibo = "zjld.weibo.newstitle"
            Scheduler.schedule(weibo ,key=str(key), 
                                data=data, interval=21600, reset=True)
            weixin = "zjld.sogou.keywords"
            Scheduler.schedule(weixin ,key=str(key), 
                                data=data, interval=7200, reset=True)

    def crawl(self): 
        worlds = str(self.key)
        world = '+'.join(worlds.split(','))
        data = self.data
        homepage = "http://news.baidu.com/ns?ct=0&rn=20&ie=utf-8&bs="+world+"&\
                    rsv_bp=1&sr=0&cl=2&f=8&prevct=no&tn=news&word="+world
        # homepage = "http://news.baidu.com/ns?ct=0&rn=20&ie=utf-8&bs=intitle:\
        #             ("+world+")&rsv_bp=1&sr=0&cl=2&f=8&\
        #             prevct=no&tn=newstitle&word="+world
        homepage = clear_space(homepage)
        html_stream = _get_url(str(homepage))
        xp_content = "//div[@id='content_left']/ul/li"
        items = HandleContent.get_item(html_stream,xp_content)
        xp_title = "h3[@class='c-title']//text()"
        xp_str = "div//p[@class='c-author']/text()"
        #xp_str = "div[@class='c-title-author']/text()"
        xp_url = "h3[@class='c-title']/a/@href"
        xp_count = "div//span[@class='c-info']/a[@class='c-more_link']/text()"
        for item in items:
            date = new_time()
            title = HandleContent.get_context(item,xp_title,text=True)
            pt_text = HandleContent.get_context(item,xp_str,text=True)
            publisher = HandleContent.get_author(pt_text, xp_text='', STR=True)
            pubtime = HandleContent.find_pubtime(pt_text)
            pubtime = local2utc(pubtime) if pubtime else date.get('utctime')
            url = HandleContent.get_context(item,xp_url,text=True)
            count = HandleContent.get_context(item,xp_count,text=True)
            try:
                count = int(count.split(u'条相同新闻',1)[0]) if count else 0
            except:
                count =0
            crawl_data = {}
            crawl_data = {
            #    'url': url,
                'title': title,
                'pubtime': pubtime,
                'source': u'baidu',
                'publisher': publisher,
                'count': str(count),
                'key': world,
                'source_type': data.get('source_type', ''),
                
            }
            # print title,url
            Scheduler.schedule(ContentCrawler.type ,key=url,
                                 data=crawl_data)

class ContentCrawler(Crawler):
    type = "zjld.baidu.newscontent"  

    def crawl(self): 
        data = self.data
        url = str(self.key)
        html_stream = _get_url(url)
        soup = Readability(html_stream.text, url)
        content = soup.content
        # soup = HandleContent.get_BScontext(html_stream)
        comment = {}
        try:
            # content = soup.find_all(['p','span','h3','h4','h5'])     
            # content = clear_a(content)
            text = HandleContent.get_BScontext(content, text=True).text
            comment['content'] = clear_space(text)
        except:
            content = ''
            pass
       # comment['key'] = data.get('key','')
        comment['count'] = data.get('count','')
        crawl_data = {}
        date = new_time()
        crawl_data = {
            'title': data.get('title', ''),
            'pubtime': data.get('pubtime', datetime.utcfromtimestamp(0)),
            'source': 'baidu',
            'publisher': data.get('publisher'),
            'crtime_int': date.get('crtime_int'),
            'crtime': date.get('crtime'),
            'origin_source': u'百度搜索',
            'url': url,
            'key': data.get('key', ''),
            'type': u'元搜索',
            'source_type': data.get('source_type', ''),
            'content': content,
            'comment': comment,
        }
        if comment['content']:
            model = SearchArticleModel(crawl_data)
            export(model)
     
if __name__ == "__main__":
    # key = '通用点火系统缺陷致大规模召回危机'
    # EventCrawler(key=key).crawl()
    url = 'http://china.huanqiu.com/hot/2015-03/5990111.html'
    ContentCrawler(key=url).crawl()
    # EventCrawler.init()
