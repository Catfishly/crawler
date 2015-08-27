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

#广东广州质监局 gzq
def _get_url(url, code='utf-8'):
    html_stream = get_urls_re(url, time = 6)
    if True:
        html_stream.encoding = 'GBK'
    else:
        html_stream.encoding = get_charset(html_stream.text)
    return html_stream

class FirstCrawler(Crawler):
    type = "zjld.gzq.firstlvl"

    @staticmethod
    def init(conf=None):
        Scheduler.schedule(FirstCrawler.type, interval=10800, reset=True)

    def crawl(self):
        homepage = "http://www.gzq.gov.cn/"
        html_stream = _get_url(homepage)
        for item in HandleUrl.get_url(html_stream.text):
            item = HandleUrl.judge_url(item,homepage)
            text = '^(http|https).+(public).+.+\d$'
            url_t = re.match(text, item)
            data = {}
            if url_t != None:
                # print item.encode('utf-8')
                Scheduler.schedule(ContentCrawler.type, key=item, data=data)
            else:
                pass

class ContentCrawler(Crawler):
    type = "zjld.gzq.newscontent"

    def crawl(self):

        url = self.key
        html_stream = _get_url(url)
        soup = HandleContent.get_BScontext(html_stream)
        content = soup.find_all('td',id='td_news_content')
        content = clear_label(content, root=url)
        comment = {}
        text = HandleContent.get_BScontext(content, text=True).text
        comment['content'] = clear_space(text)
        xp_title = "//tr/td[@class='content-title']/div/text()"    
        xp_putime = "//tr/td[@class='bottom-line-gray']/text()"
      #  xp_author = "//ul/li[@class='show_date']/text()"
        title = HandleContent.get_title(html_stream, xpath=xp_title)
        pubtime = HandleContent.get_pubtime(html_stream, xpath=xp_putime)
      #  author = HandleContent.get_author(html_stream, xpath=xp_author)
        date = new_time()
        crawl_data = {
            'url': url,
            'province': u'广东',
            'city': u'广州',
            'title': title,
            'content': content,
            'pubtime': pubtime,
            'crtime_int': date.get('crtime_int'),
            'crtime': date.get('crtime'),
            'source': u'gzq',
            'publisher': u'广东广州质监局',
            'source_type': u'质监局',
          #  'origin_source': u'福建质监局',
          #  'author': author,
            'type': u'文章',
            'comment': comment,
        }
        # print title.encode('utf-8'), pubtime
        # print comment['content'].encode('utf-8')
        # print content.encode('utf-8')
        model = ZjldArticleModel(crawl_data)
        export(model)

        
if __name__ == '__main__':
    # FirstCrawler().crawl()
    url = 'http://www.gzq.gov.cn/public/content.jsp?catid=16&id=39993'
    ContentCrawler(key=url).crawl()