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

#广东佛山质监局 fsjsjd
def _get_url(url, code='utf-8'):
    html_stream = get_urls_re(url, time = 6)
    if True:
        html_stream.encoding = 'gb2312'
    else:
        html_stream.encoding = get_charset(html_stream.text)
    return html_stream

class FirstCrawler(Crawler):
    type = "zjld.fsjsjd.firstlvl"

    @staticmethod
    def init(conf=None):
        Scheduler.schedule(FirstCrawler.type, interval=10800, reset=True)
        
    def crawl(self):
        homepage = "http://www.fsjsjd.gov.cn/"
        html_stream = _get_url(homepage)
        for item in HandleUrl.get_url(html_stream.text):
            xp_putime = "//a[@href='%s']/parent::*/text()"%item
            pubtime = HandleContent.get_pubtime(html_stream, xpath=xp_putime)
            item = HandleUrl.judge_url(item,homepage)
            text = '^(http|https).+\d\.(htm|html|net)$'
            url_t = re.match(text, item)
            data = {}
            if url_t != None:
                data['pubtime'] = pubtime
                Scheduler.schedule(ContentCrawler.type, key=item, data=data)
            else:
                pass

class ContentCrawler(Crawler):
    type = "zjld.fsjsjd.newscontent"

    def crawl(self):

        url = self.key
        data = self.data
        html_stream = _get_url(url)
        soup = HandleContent.get_BScontext(html_stream)
        content = soup.find_all('div',id='right-text_d')
        content = clear_label(content, root=url)
        comment = {}
        text = HandleContent.get_BScontext(content, text=True).text
        comment['content'] = clear_space(text)
        xp_title = "//div[@id='right-title_d']//text()"    
        xp_putime = "//div[@class='article']/p[@class='info']/span/text()"
      #  xp_author = "//ul/li[@class='show_date']/text()"
        title = HandleContent.get_title(html_stream, xpath=xp_title)
        pubtime = HandleContent.get_pubtime(html_stream, xpath=xp_putime)
      #  author = HandleContent.get_author(html_stream, xpath=xp_author)
        date = new_time()
        crawl_data = {
            'url': url,
            'province': u'广东',
            'city': u'佛山',
            'title': title,
            'content': content,
            'pubtime': data.get('pubtime', pubtime),
            'crtime_int': date.get('crtime_int'),
            'crtime': date.get('crtime'),
            'source': u'fsjsjd',
            'publisher': u'广东佛山质监局',
            'source_type': u'质监局',
          #  'origin_source': u'福建质监局',
          #  'author': author,
            'type': u'文章',
            'comment': comment,
        }
        # print title.encode('utf-8'), '---',crawl_data['pubtime']
        # print comment['content'].encode('utf-8')
        model = ZjldArticleModel(crawl_data)
        export(model)

        
if __name__ == '__main__':
    FirstCrawler().crawl()
    # url = 'http://www.fsjsjd.gov.cn/zjxw/zhgzdt/201503/t20150331_5083329.html'
    # ContentCrawler(key=url).crawl()