#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
root_mod = '/home/xxguo/Project/crawler'
sys.path.append(root_mod)

import re
reload(sys)
sys.setdefaultencoding('utf-8')
import time, random
from bs4 import BeautifulSoup
from urllib import quote ,unquote
from models.weibo.model import WeiboArticleModel, WeiboHotModel
from models.search.model import SearchArticleModel
from scheduler.crawler import Crawler, export, Scheduler 
from crawlerimpl.weixin.processdata import HandleUrl, new_time, clear_label, \
        HandleContent, get_urls_re, get_charset, change_to_json, clear_space

def _get_url(url):
    html_stream = get_urls_re(url, time = 6)
    if True:
        html_stream.encoding = "utf-8"
    else:
        html_stream.encoding = get_charset(html_stream.text)
    return html_stream

class FirstCrawler(Crawler):
    type = "zjld.weibo.firstlvl"

    @staticmethod
    def init(conf=None):

        from xlutils.copy import copy
        import xlrd
        import os
        SRC_PATH = os.path.dirname(__file__)
        bk = xlrd.open_workbook(os.path.join(SRC_PATH,
                                 "../../file/weibo.xls"))
        sh = bk.sheet_by_name('Sheet1')
        nrows = sh.nrows
        ncols = sh.ncols
        for i in xrange(1,nrows):
            data = {}
            data = {
                'publisher': sh.cell_value(i,3).strip(),
                'province': sh.cell_value(i,0).strip(),
                'city': sh.cell_value(i,1).strip(),
                'district': sh.cell_value(i,2).strip()
            }
            key = str(int(sh.cell_value(i,5))).strip()        
            Scheduler.schedule(FirstCrawler.type ,key=key, 
                                data=data, interval=3600, reset=True)

    def crawl(self):
        world = self.key
        data = self.data
        homepage = "http://api.weibo.cn/2/profile?\
                    gsid=_2A254IZdKDeTxGeRM7lUR8CnKyT2IHXVZdq2CrDV6PUJbrdAKLUf7kWptw4_No8F1OjQMCarBH4hZxZcrwA..&\
                    wm=3333_2001&i=27bd163&b=1&from=1051293010&c=iphone&v_p=18&skin=default&\
                    v_f=1&s=d2672a12&luicode=10000194&uid="+str(world)
        # homepage = "http://api.weibo.cn/2/profile?gsid=4wMJ47123kZuG0fKGxlRC15McKa50&uid="+str(world)+"&\
        #             wm=3333_2001&i=27bd163&b=0&from=1052093010&checktoken=c54259b09129d101b9669b5d93a04c0e&\
        #             c=iphone&v_p=18&skin=default&v_f=1&s=8a12fc6c&did=38d63734cc7427ebb2cb77612c1948cf&\
        #             lang=zh_CN&ua=iPhone7,2__weibo__5.2.0__iphone__os8.2&uicode=10000198&uid="+str(world)+\
        #             "&featurecode=10000085&luicode=10000003"

        homepage = clear_space(homepage)
        html_stream = _get_url(homepage)
        json_stream = change_to_json(str(html_stream.text))
        containerid = json_stream['tabsInfo']['tabs'][1]['containerid']
        data['id'] = str(world)
        Scheduler.schedule(ContentCrawler.type, key=containerid, data=data,
                             reset=True, interval=10800)

class ContentCrawler(Crawler):
    type = "zjld.weibo.newscontent"  

    def crawl(self): 
        key = str(self.key)
        data = self.data
        homepage = "http://api.weibo.cn/2/cardlist?\
                    gsid=_2A254IZdKDeTxGeRM7lUR8CnKyT2IHXVZdq2CrDV6PUJbrdAKLUf7kWptw4_No8F1OjQMCarBH4hZxZcrwA..&\
                    wm=3333_2001&i=27bd163&b=1&from=1051293010&c=iphone&v_p=18&skin=default&\
                    v_f=1&s=d2672a12&lang=zh_CN&ua=iPhone7,2__weibo__5.1.2__iphone__os8.1.3&\
                    uicode=10000198&featurecode=10000085&luicode=10000003&count=20&\
                    extparam=100103type=1&cuid=2257007621&sid=t_wap_ios&category=1&\
                    pos=1_-1&wm=3333_2001&containerid="+key+"_-_WEIBO_SECOND_PROFILE_WEIBO&\
                    fid="+key+"_-_WEIBO_SECOND_PROFILE_WEIBO&lfid=100103type%3D1&\
                    sourcetype=page&lcardid=user&page=1"
        # homepage = "http://api.weibo.cn/2/guest/cardlist?gsid=4wMJ47123kZuG0fKGxlRC15McKa50&uid=1001503246310&\
        #             wm=3333_2001&i=27bd163&b=0&from=1052093010&checktoken=c54259b09129d101b9669b5d93a04c0e&c=iphone&\
        #             v_p=18&skin=default&v_f=1&s=8a12fc6c&did=38d63734cc7427ebb2cb77612c1948cf&lang=zh_CN&ua=iPhone7,\
        #             2__weibo__5.2.0__iphone__os8.2&uid=1001503246310&extparam=100103\
        #             type%3D1%26q%3D%E5%8C%97%E4%BA%AC%E5%AE%89%E7%9B%91%26t%3D0%26sid%3Dt_wap_ios%26category%3D1%26pos%3D1_-1%26wm%3D3333_2001&\
        #             count=20&luicode=10000003&containerid="+key+"_-_WEIBO_SECOND_PROFILE_WEIBO&featurecode=10000085&\
        #             uicode=10000198&fid="+key+"_-_WEIBO_SECOND_PROFILE_WEIBO&checktoken=\
        #             c54259b09129d101b9669b5d93a04c0e&did=38d63734cc7427ebb2cb77612c1948cf&page=1"
        homepage = clear_space(homepage)
        html_stream = _get_url(homepage)     
        json_stream = change_to_json(str(html_stream.text))
        cards = json_stream['cards']
        for item in cards:
            scheme = re.search(r'=(.+?)$', item.get('scheme',''))
            scheme = scheme.group(1) if scheme else ''
            url = "http://weibo.com/%s/%s?type=comment"%(data.get('id', ''),
                     scheme)
            item = item.get('mblog',{})
            item = item.get('retweeted_status',item)
            text = item.get('text','')
            title = re.search(ur'【(.+?)】', text)
            title = title.group(1) if title else ''
            if not title:
                title = re.search(ur'#(.+?)#', text)
                title = title.group(1) if title else text[0:20]+'...'
            subtitle = re.search(ur'#(.+?)#', text)           
            subtitle = subtitle.group(1) if subtitle else ''
            pubtime = item.get('created_at', '')
            pubtime = HandleContent.strformat(str(pubtime))
            reposts_count = item.get('reposts_count', '')
            comments_count = item.get('comments_count', '')
            attitudes_count = item.get('attitudes_count', '')
            thumbnail_pic = item.get('thumbnail_pic', '')
            bmiddle_pic = item.get('bmiddle_pic', '')
            original_pic = item.get('original_pic', '')
            mid = item.get('mid', '')
            author = item.get('user',{}).get('name','')
            comment = {}
            comment = {
                'reposts_count': str(reposts_count),
                'attitudes_count': str(attitudes_count),
                'comments_count': str(comments_count)
            }
            crawl_data = {}
            subtitles = []
            subtitles.append(subtitle)
            date = new_time()
            crawl_data = {
                'province': self.data.get('province',''),
                'city': self.data.get('city',''),
                'district': self.data.get('district',''),
                'url': url,
                'title': title,
                'subtitle': subtitles,
                'content': text,
                'pubtime': pubtime,
                'crtime_int': date.get('crtime_int'),
                'crtime': date.get('crtime'),
                'source': 'weibo',
                'publisher': self.data.get('publisher',''),
                'author': author,
                'origin_source': u'新浪微博',
                'type': u'微博',
                'comment': comment
            }
            model = WeiboArticleModel(crawl_data)
            if export(model):
                againt_data = {}
                againt_data = {
                    'wid': model['id'],
                    'type': u'微博',
                    'expire': date.get('crtime_int')/1000000 + 604800,
                }
                Scheduler.schedule(AgainCrawler.type, key=mid, data=againt_data,
                                 reset=True, interval=21600)
            else:
                pass

class AgainCrawler(Crawler):
    type = "weibo_hot.weibo.hot"

    def crawl(self): 
        key = str(self.key)
        data = self.data
        homepage = "http://api.weibo.cn/2/guest/statuses_extend?v_f=2&\
        uid=1001979296366&lfid=230584&checktoken=70b77970ea4b0fb23e95549430204e44&\
        c=android&wm=2468_1001&did=006997cad1bdce0960777445e8b8fed211d91950&\
        luicode=10000228&from=1051295010&lang=zh_CN&lcardid="+key+"&\
        skin=default&i=5c7d1a1&id="+key+"&fromlog=230584&s=9bad809a&\
        gsid=4wkmda923WBtPcv1v5vMS15OcAo5U&ua=HUAWEI-HUAWEI%20T8950__weibo__5.1.2__android__android4.0.4&\
        oldwm=2468_1001&is_recom=-1&uicode=10000002"
        homepage = clear_space(homepage)
        html_stream = _get_url(homepage)    
        json_stream = change_to_json(str(html_stream.text))
        crawl_data = {}
        reposts_count = json_stream.get('reposts_count', 0)
        comments_count = json_stream.get('comments_count', 0)
        attitudes_count = json_stream.get('attitudes_count', 0)
        date = new_time()
        crawl_data = {
            'id': data.get('wid'),
            'reposts': reposts_count,
            'comments': comments_count,
            'likes': attitudes_count,
            'type': data.get('type'),
            'crtime_int': date.get('crtime_int'),
            'expire': data.get('expire')
        }
        model = WeiboHotModel(crawl_data)
        export(model)

class EventCrawler(Crawler):
    type = "zjld.weibo.newstitle"

    def crawl(self):
        key = str(self.key)
        data = self.data
        homepage = "http://m.weibo.cn/p/index?containerid=100103type%3D36%26q%3D"+key+\
                    "%26weibo_type%3Dlongwb&title=%E9%95%BF%E5%BE%AE%E5%8D%9A"
        homepage = clear_space(homepage)
        html_stream = _get_url(homepage)
        time.sleep(random.randint(0,5))
        url_list = re.findall(r"(?<=scheme\":\").+?(?=\")", 
                html_stream.text)
        data.update({
            'key': key
        })
        for item in url_list:
            item = unquote(item)
            cid = re.search(r'.+\/p\/(.+?)\?.+', item)
            if cid:
                Scheduler.schedule(TopicCrawler.type, key=cid.group(1), data=data)
            else:
                continue

class TopicCrawler(Crawler):
    type = "zjld.weibo.newsarticle" 

    def crawl(self):
        key = self.key
        data = self.data
        homepage = "http://card.weibo.com/article/aj/articleshow?cid="+ key
        url = "http://weibo.com/p/"+ key
        html_stream = _get_url(homepage)    
        json_stream = change_to_json(str(html_stream.text))
        html_stream = json_stream['data']['article']
        soup = HandleContent.get_BScontext(html_stream, text=True)
        title = soup.select('.title')[0].text
        pubtime = soup.select('.time')[0].text
        pubtime = HandleContent.strformat(str(pubtime))
        content = soup.select('.WBA_content')[0]
        content = clear_label(list(content))
        comment = {}
        text = HandleContent.get_BScontext(content, text=True).text
        comment['content'] = clear_space(text)
        publishers = soup.select('.S_link2')
        # author = reduce(lambda x, y: x + y, [item.text for item in authors])
        try:
            publisher = publishers[1].text if len(publishers)> 1 else publishers[0].text
        except:
            publisher = ''
        crawl_data = {}
        date = new_time()
        crawl_data = {
            'title': title,
            'pubtime': pubtime,
            'source': 'weibo',
            'publisher': publisher,
            'crtime_int': date.get('crtime_int'),
            'crtime': date.get('crtime'),
            'origin_source': u'微博搜索',
            'url': url,
            'key': data.get('key', ''),
            'type': u'元搜索',
            'source_type': data.get('source_type', ''),
            'content': content,
            'comment': comment,
        }
        model = SearchArticleModel(crawl_data)
        export(model)

if __name__ == "__main__":
    EventCrawler(key=u'美《消费者报告》年度车型报告：雷克萨斯最可靠，娱乐系统不可靠').crawl()

    # TopicCrawler(key='2304184a883a610102vj3c').crawl()
    # FirstCrawler(key='2769670731').crawl()
    #FirstCrawler.init()1076032417860437 1076032769670731
    # ContentCrawler(key='1076032769670731',data={'id':'2769670731'}).crawl()
    # import uuid
    # date = new_time()
    # data = {
    #     "wid" : "0286bd94-d1fe-11e4-aaaa-00e0b616d646",
    #     "type" : "微博",
    #     'expire': date.get('crtime_int')/1000000 + 604800,
    # }
    # AgainCrawler(key='3818861645835691',data=data).crawl()

    # import time
    # print time.time()
    # print date.get('crtime_int')/1000000 +604800
