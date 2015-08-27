#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
root_mod = '/home/xxguo/Project/crawler'
sys.path.append(root_mod)

import re
from lxml import etree
from article.articles import get_titles,get_publish_times
from scheduler.crawler import Crawler, export, Scheduler
from models.zjld.model import ZjldArticleModel
from utils.readability import Readability
from crawlerimpl.zjld.processdata import HandleUrl , HandleContent, \
        get_urls_re, get_charset, clear_label, clear_space, new_time, \
        local2utc, get_code, clear_a

def _get_url(url, code='utf-8'):
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

class FirstCrawler(Crawler):
    type = "zjld.yuqing.firstlvl"

    @staticmethod
    def init(conf=None):
        from xlutils.copy import copy
        import xlrd
        import os
        SRC_PATH = os.path.dirname(__file__)
        bk = xlrd.open_workbook(os.path.join(SRC_PATH,
                                 "../../file/newyuqing.xls"))
        sh = bk.sheet_by_name('Sheet1')
        nrows = sh.nrows
        ncols = sh.ncols
        for i in range(1,nrows):
            data = {}
            types = sh.cell_value(i,1).strip()
            province = sh.cell_value(i,2).strip()
            city = sh.cell_value(i,3).strip()
            district = sh.cell_value(i,4).strip()
            data = {
                'type': types,
                'province': province,
                'city': city,
                'district': district,
                'publisher': (province+city+district+types)
            }
            key =  sh.cell_value(i,5).strip()    
            # print data['publisher'].encode('utf-8') 
            if key == '':
                continue
            Scheduler.schedule(FirstCrawler.type ,key=key, 
                                data=data, interval=14800, reset=True)

    def crawl(self):
        homepage = self.key
        data = self.data
        html_stream = _get_url(homepage)
        for item in HandleUrl.get_url(html_stream.text):
            item = HandleUrl.judge_url(item,homepage)
            if re.search('(ndex)',item):
                continue
            text = '^(http|https).+\d\.(htm|html|net|php)$'
            url_t = re.match(text, item)
            if url_t != None:
                Scheduler.schedule(ContentCrawler.type, key=item, data=data)
            else:
                pass

class ContentCrawler(Crawler):
    type = "zjld.yuqing.newscontent"

    def crawl(self): 
        data = self.data
        url = self.key
        html_stream = _get_url(url)
        title = get_titles(html_stream)
        pubtime = local2utc(get_publish_times(html_stream))
        soup = Readability(html_stream.text, url)
        content = soup.content
        # soup = HandleContent.get_BScontext(html_stream)
        comment = {}
        try:
            text = HandleContent.get_BScontext(content, text=True).text
            comment['content'] = clear_space(text)
        except:
            content = ''
            pass
       # comment['key'] = data.get('key','')
        # comment['count'] = data.get('count','')
        crawl_data = {}
        date = new_time()
        crawl_data = {
            'url': url,
            'province': data.get('province'),
            'city': data.get('city', u''),
            'district': data.get('district', u''),
            'title': title,
            'content': content,
            'pubtime': pubtime,
            'crtime_int': date.get('crtime_int'),
            'crtime': date.get('crtime'),
            'source': u'yuqing',
            'publisher': data.get('publisher', u''),
            'source_type': data.get('type'),
          #  'origin_source': u'福建质监局',
          #  'author': author,
            'type': u'文章',
            'comment': comment,
        }
        if comment['content']:
            model = ZjldArticleModel(crawl_data)
            export(model)
        
if __name__ == '__main__':
    # key = 'http://es.egs.gov.cn/structure/index.htm'
    # FirstCrawler(key=key).crawl()
    FirstCrawler().init()
    # url = 'http://www.sdnews.com.cn/gov/zfcg/201410/t20141029_1766384.html'
    # ContentCrawler(key=url).crawl()