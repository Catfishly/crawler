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

#中国质量新闻网 cqn
def _get_url(url, code='utf-8'):
    html_stream = get_urls_re(url, time = 6)
    if True:
        html_stream.encoding = "gb2312"
    else:
        html_stream.encoding = get_charset(html_stream.text)
    return html_stream

class FirstCrawler(Crawler):
    type = "zjld.cqn.firstlvl"

    @staticmethod
    def init(conf=None):
        # pass
        Scheduler.schedule(FirstCrawler.type, interval=10800, reset=True)

    def crawl(self):
        one = "http://www.cqn.com.cn/news/zjpd/zljd/Index.html"
        two = "http://www.cqn.com.cn/news/xfpd/ccgg/Index.html"
        three = "http://www.cqn.com.cn/news/zjpd/zjdt/Index.html"
        #http://www.cqn.com.cn/news/zhuanti/Index.html
        self.firstcrawler(one)
        self.getchildurl(two)
        self.getchildurl(three)

    def firstcrawler(self, homepage):
        html_stream = _get_url(homepage)
        list_url = []
        for item in HandleUrl.get_url(html_stream.text):
            # url_res = HandleUrl.judge_url(item,homepage)
            # if url_res == ''
            #     continue
            text = '.+\/(bj|tj|hb|sx|nmg|ln|jl|hlj|sh|js|zj|ah|fj|jx|sd|hn|hub|hun|gd|gx|hain|cq|sc|gz|yn|xz|shx|gs|qh|nx|xj)\/Index.html$'
            url_t = re.match(text,item)
          #  url_t = HandleUrl.judge_url(homepage,url_t)
            if url_t != None and (item not in list_url):
                self.getchildurl(HandleUrl.join_url_path(homepage,item))
                list_url.append(item)

    def getchildurl(self, url,data={}):
        html_stream = _get_url(url)
    
        for item in HandleUrl.get_url(html_stream.text):
            text = '^(http|https).+(news)\/(zjpd|xfpd|zhuanti|zgzlb).+\d\.(htm|html|net)$'
            url_t = re.match(text, item)
            if url_t != None:
                # ContentCrawler(key=item).crawl()
                # print item
                Scheduler.schedule(ContentCrawler.type, key=item, data=data)
            else:
                pass

class ContentCrawler(Crawler):
    type = "zjld.cqn.newscontent"

    def crawl(self):

        url = self.key
        html_stream = _get_url(url)
        soup = HandleContent.get_BScontext(html_stream)
        content = soup.find_all('div','Index_ShowDetail_Content')
        content = clear_label(content, root=url)
        comment = {}
        text = HandleContent.get_BScontext(content, text=True).text
        comment['content'] = clear_space(text)
        xp_title = "//div[@class='Index_ShowDetail_Title']/h1/text()"    
        xp_putime = "//div[@class='Index_ShowDetail_Time']//text()"
        title = HandleContent.get_title(html_stream, xpath=xp_title)
        pubtime = HandleContent.get_pubtime(html_stream, xpath=xp_putime)
        date = new_time()
        crawl_data = {
            'url': url,
            'province': u'全国',
            'title': title,
            'content': content,
            'pubtime': pubtime,
            'publisher': u'中国质量新闻网',
            'crtime_int': date.get('crtime_int'),
            'crtime': date.get('crtime'),
            'source': 'cqn',
            'source_type': u'中国质量新闻网',
           # 'origin_source': u'中国质量新闻网',
            'type': u'文章',
            'comment': comment,
        }
        model = ZjldArticleModel(crawl_data)
        export(model)

if __name__ == "__main__":
    # url = 'http://www.cqn.com.cn/news/zggmsb/diyi/1018827.html'
    # ContentCrawler(key=url).crawl()
    FirstCrawler().crawl()


