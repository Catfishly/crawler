#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
root_mod = '/home/xxguo/Project/crawler'
sys.path.append(root_mod)

import re
from lxml import etree
#from bs4 import BeautifulSoup
from scheduler.crawler import Crawler, export, Scheduler
from models.zjld.model import ZjldArticleModel
from processdata import HandleUrl , HandleContent, get_urls_re, \
        get_charset, clear_label, clear_space, new_time

#江西质监局 jxzj
def _get_url(url, code='utf-8'):
    html_stream = get_urls_re(url, time = 6)
    if True:
        html_stream.encoding = 'GBK'
    else:
        html_stream.encoding = get_charset(html_stream.text)
    if html_stream.status_code != 200:
        return html_stream
    return html_stream

class FirstCrawler(Crawler):
    type = "zjld.jxzj.firstlvl"

    @staticmethod
    def init(conf=None):
       # pass
        Scheduler.schedule(FirstCrawler.type, interval=10800, reset=True)

    def crawl(self):
        homepage = "http://www.jxzj.gov.cn/jxzj/index.html"
        html_stream = _get_url(homepage)
        for item in HandleUrl.get_url(html_stream.text):
            item = HandleUrl.judge_url(item,homepage)
            text = '^(http|https).+(news).+\.(htm|html|net)$'
            url_t = re.match(text, item)
            data = {}
            if url_t != None:
                Scheduler.schedule(ContentCrawler.type, key=item, data=data)
            else:
                pass

class ContentCrawler(Crawler):
    type = "zjld.jxzj.newscontent"

    def crawl(self):

        url = self.key
        html_stream = _get_url(url)
        soup = HandleContent.get_BScontext(html_stream)
        content = soup.find_all('li','show_con')
        content = clear_label(content, root=url)
        comment = {}
        text = HandleContent.get_BScontext(content, text=True).text
        comment['content'] = clear_space(text)
        xp_title = "//ul/li[@class='show_title']/text()"    
        xp_putime = "//ul/li[@class='show_date']/text()"
        xp_author = "//ul/li[@class='show_date']/text()"
        title = HandleContent.get_title(html_stream, xpath=xp_title)
        pubtime = HandleContent.get_pubtime(html_stream, xpath=xp_putime)
        author = HandleContent.get_author(html_stream, xpath=xp_author)
        date = new_time()
        crawl_data = {
            'url': url,
            'province': u'江西',
         #   'city': u'杭州',
            'title': title,
            'content': content,
            'pubtime': pubtime,
            'crtime_int': date.get('crtime_int'),
            'crtime': date.get('crtime'),
            'source': u'jxzj',
            'publisher': u'江西质监局',
            'source_type': u'质监局',
        #    'origin_source': u'江西质监局',
            'author': author,
            'type': u'文章',
            'comment': comment,
        }
        model = ZjldArticleModel(crawl_data)
        export(model)
        
if __name__ == '__main__':
    # FirstCrawler().crawl()
    url = 'http://www.jxzj.gov.cn/html/news/1000010246/100001024610251/2015-03/82442.html'
    ContentCrawler(key=url).crawl()