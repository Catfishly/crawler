#!/usr/bin/python
#encoding=utf-8

import sys
root_mod = '/home/xxguo/Project/crawler'
sys.path.append(root_mod)

reload(sys)
sys.setdefaultencoding('utf-8')
import re
import requests
import time
import random
from urllib import quote, unquote
from xml.etree import ElementTree
from lxml import etree
#from bs4 import BeautifulSoup
from models.weixin.model import WeixinArticleModel
from models.search.model import SearchArticleModel
from scheduler.crawler import Crawler, export, Scheduler
from processdata import HandleUrl , HandleContent, get_urls_re, new_time,\
        get_charset, change_to_json, clear_label, getIP, clear_space

def _get_url(url, code='utf-8', cookie=''):
    html_stream = get_urls_re(url, time = 6, cookie=cookie)
    if True:
        html_stream.encoding = code
    else:
        html_stream.encoding = get_charset(html_stream.text)
    if html_stream.status_code != 200:
        return html_stream
    return html_stream

# def create_cookies():
#     cookies = {}
#     global listips
#     UT = time.time()*1000
#     cookies = {
#         'SUID': '6A7A6077260C930A0000000054F1B1D5',
#         'SNUID': '849626F8DCD9CD962F627F83DD7B02C7',
#         'IPLOC': 'CN4201',
#         'ABTEST': '1|'+str(UT)+'|v1',
#         'SUIR': str(UT),
#         'SUV': str(UT+random.randint(100, 1000))
#         }

#     return cookies

# def get_SNUID(url):
#     global listips
#     s = requests.Session()
#     i_headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN;\
#                  rv:1.9.1) Gecko/20090624 Firefox/3.5",
#                  "Referer": 'http://weixin.sogou.com'}
#     IPS = random.choice(listips.keys())
#     s.proxies = {
#         'http': IPS
#     }
#     count = 0
#     while count < 3:
#         try:
#             html_stream = s.get(url, timeout=5, headers=i_headers)
#          #   print html_stream.text
#             mtre = r".+document\.cookie = \"SNUID=(.+?);.+"
#             snuid = re.search(mtre,html_stream.text,re.DOTALL).group(1)
#             print '=================',snuid
#             print '-----------'

#         except:
#             count += 1
#             print 'type ',
#             print 'listips[ipds]',listips[IPS]
#             listips.pop(IPS)
#             if not listips:
#                 listips = getIP(10)
#         else:
#             break

def get_cookies():
    initial_cook = [
        {
            'ABTEST':'7|1430810607|v1',
            'IPLOC':'CN4201',
            'PHPSESSID':'bjbvji1318u2mi6smp6g6tba46',
            'SNUID':'C23CCCD8AFAABAFE3AACCBF8AF541E29',
            'SUID':'6C9262776A20900A0000000055486FF4',
            'SUID':'6C9262777E23900A0000000055486FF4',
            'SUIR':'1430810612',
            'SUV':'00E87B617762926C55487004EB218696'
        },
        {
            'ABTEST':'0|1430818728|v1',
            'IPLOC':'CN4201',
            'PHPSESSID':'sp4sfq7u8ns6sotmlnedcm0v57',
            'SNUID':'F30DFDD79FA5B5F2D22405A1A0AD170F',
            'SUID':'6C9262776F1C920A0000000055488FA8',
            'SUID':'6C9262774C1C920A0000000055488FA9',
            'SUIR':'1430818729',
            'SUV':'00AC7B5C7762926C55488FA0C59A5426'
        },
        {
            'ABTEST':'0|1430900634|v1',
            'IPLOC':'CN4201',
            'PHPSESSID':'jk988nfggq1vlmst38q84tubs7',
            'SNUID':'53ECE208807A6AE50483D22F80DEA976',
            'SUID':'D39362776A20900A000000005549CF9A',
            'SUID':'D39362771524900A000000005549CFB0',
            'SUIR':'53ECE208807A6AE50483D22F80DEA976',
            'SUV':'00647D92776293D35549CFB042FDE894'
        },
        {
            'ABTEST':'8|1430903106|v1',
            'IPLOC':'CN4201',
            'PHPSESSID':'4gbjmmq9ivgeqdkjcr1vgcauh6',
            'SNUID':'E0A051443236275425C1D5BA3359F410',
            'SUID':'D39362776A20900A000000005549D942',
            'SUID':'D39362776A28920A000000005549D942',
            'SUIR':'1430903106',
            'SUV':'000675F9776293D35549D9434CD22518'
        }

    ]
    cookies = []
    print 'weixin get get_cookies()'
    for i in xrange(8): 
        url = 'http://weixin.sogou.com/weixin?query=%s'%\
                random.choice('abcdefghijklmnopqrstuvwxyz')
        t = requests.get(url=url)
        text = t.cookies
        cookies_list=re.findall(r"(?<=<Cookie\s).+?=.+?(?=\sfor)",
                                str(text))
        cookie = random.choice(initial_cook)
        for item in cookies_list:
            item = item.split('=')
            cookie[item[0]] = item[1]
        if cookie.get('SNUID'):
            UT = int(time.time())-1
            cookie['SUIR'] = str(UT)
            cookie['SUV'] = str(UT*1000000+random.randint(1, 1000))
            cookies.append(cookie)
        else:
            time.sleep(random.randint(10,30))
            print 'Gets a cookies failure , file:sogou'
            cookies = []
            break
        time.sleep(random.randint(1,15))
    return cookies

clocking = 0
cookies = []
STATUS_CK = 0
class FirstCrawler(Crawler):
    type = "zjld.sogou.firstlvl"

    @staticmethod
    def init(conf=None):

        from xlutils.copy import copy
        import xlrd
        import os

        SRC_PATH = os.path.dirname(__file__)

        bk = xlrd.open_workbook(os.path.join(SRC_PATH,
                             "../../file/weixin.xls"))
        sh = bk.sheet_by_name('Sheet1')
        nrows = sh.nrows
        ncols = sh.ncols
        for i in xrange(1,nrows):
            data = {}
            data = {
                'publisher': sh.cell_value(i,0).strip(),
                'province': sh.cell_value(i,1).strip(),
                'city': sh.cell_value(i,2).strip(),
                'district': sh.cell_value(i,3).strip()
            }
            key = sh.cell_value(i,6).strip()
            Scheduler.schedule(FirstCrawler.type ,key=key,
                                 data=data, interval=28800, reset=True)

#         event = xlrd.open_workbook(os.path.join(SRC_PATH,
#                              "../../file/event.xls"))
#         et = event.sheet_by_name('Sheet1')
#         nrows = et.nrows
#         for i in xrange(1,nrows):
#             data = {}
#             data = {
# #                'keywords': sh.cell_value(i,0).strip(),
#         #        'brief': et.cell_value(i,1).strip(),
#             }
#             keys = et.cell_value(i,0).strip()
#    #         print keys.encode('utf-8')
#             Scheduler.schedule(KeywordsCrawler.type ,key=keys,
#                                  data=data, interval=7200, reset=True)


        # global cookies
        # global clocking
        # clocking = int(time.strftime('%H',time.localtime(time.time())))
        # cookies = get_cookies()


    def crawl(self):
        global cookies
        global clocking
        global STATUS_CK
        TIME = time.time()
        hour = time.strftime('%H',time.localtime(TIME))
        if cookies == [] and TIME > STATUS_CK:
            print 'wait-----------To obtain cookie one '
            STATUS_CK = TIME + 35200
            clocking = hour
            cookies = get_cookies()
        elif not cookies:
            print 'Gets a cookies failure'
            # STATUS_CK = TIME + 35200
            return 
        elif int(hour)%2 == 0 and clocking != hour:
            print 'wait-----------To obtain cookie'
            clocking = hour
            cookies = []
            cookies = get_cookies()
        
        cookie = random.choice(cookies)
        world = self.key
        data = self.data
        homepage = "http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid=%s&repp=1"%str(world)
        html_stream = _get_url(homepage ,cookie=cookie)
        # re.findall(")")
        mtre = "sogou.weixin.gzhcb\((.*)\)"
        match = re.search(mtre, html_stream.text).group(1)
        all_xml = change_to_json(str(match)).get('items',{})
        for item in all_xml:
            item = item.replace('\"gbk\"','\"utf-8\"')
            root = ElementTree.fromstring(item)
            geturl = root.getiterator('url')[0]
            Scheduler.schedule(ContentCrawler.type, key=geturl.text,
                                 data=data)
        time.sleep(random.randint(30,100))
    
class KeywordsCrawler(Crawler):
    type = "zjld.sogou.keywords"

    def crawl(self):
        world = self.key
        data = self.data
      #  world = str(self.key)
        data.update({
                'type': u'元搜索',
                'origin_source': u'微信搜索',
                'key': world
        })
        homepage = "http://weixin.sogou.com/weixinwap?ie=utf8&w=&\
                    type=2&t=1427703547684&s_t=&fr=sgsearch&\
                    query="+world+"&pg=webSearchList"
        homepage = clear_space(homepage)
        html_stream = _get_url(homepage)
        list_url = []
        for item in HandleUrl.get_url(html_stream.text):
            item  = HandleUrl.judge_url(item)
            if item == '':
                continue
            else:
                Scheduler.schedule(ContentCrawler.type, key=item,
                                     data=data)

class ContentCrawler(Crawler):
    type = "zjld.sogou.newscontent"  

    def crawl(self): 
        homepage = self.key
        data = self.data
        html_stream = _get_url(homepage)
        soup = HandleContent.get_BScontext(html_stream)
        content = soup.find_all('div',class_=['rich_media_content',\
                                'rich_media_thumb_wrp'])
        xp_title = "//div[@class='rich_media_area_primary']/\
                    h2[@class='rich_media_title']/text()"
        xp_putime = "//div/em[@class='rich_media_meta rich_media_meta_text']\
                    /text()"
        xp_author = "//div/em[@class='rich_media_meta rich_media_meta_text'][2]/text()"
        xp_publisher = "//div/a[@id='post-user']/text()"
        title = HandleContent.get_title(html_stream, xpath=xp_title)
        pubtime = HandleContent.get_pubtime(html_stream, xpath=xp_putime)
        author = HandleContent.get_author(html_stream, xpath=xp_author)
        publisher = HandleContent.get_author(html_stream, xpath=xp_publisher)
        comment = {}
        # con = lambda x, y: x.text.replace('\n','').replace('\r','') + \
        #                     y.text.replace('\n','').replace('\r','')
        # comment['content'] = reduce(con,content)

        content = clear_label(content, root=homepage)
        text = HandleContent.get_BScontext(content, text=True).text
        comment['content'] = clear_space(text)
        date = new_time()
        crawl_data = {}
        crawl_data = {
            'province': self.data.get('province',''),
            'city': self.data.get('city',''),
            'district': self.data.get('district',''),
            'url': homepage,
            'title': title,
            'content': content,
            'pubtime': pubtime,
            'crtime_int': date.get('crtime_int'),
            'crtime': date.get('crtime'),
            'source': 'sogou',
            'author': author,
            'publisher': self.data.get('publisher', publisher),
            'origin_source': u'微信公共账号',
            'type': u'微信',
            'comment': comment
        }
        if data.get('key'):
            crawl_data.update(data)
            model = SearchArticleModel(crawl_data)
        else:
            model = WeixinArticleModel(crawl_data)

        export(model)

if __name__ == "__main__":
   # url = 'http://mp.weixin.qq.com/s?__biz=MjM5ODExMjg0MQ==&mid=203036751&idx=4&sn=571db1c12f5780f23e293e7f88225d3f&3rd=MzA3MDU4NTYzMw==&scene=6#rd'
    url = 'http://mp.weixin.qq.com/s?__biz=MzA5Njg3NjAzNQ==&mid=202321555&idx=1&sn=1fda4ae27523111ce6e127e0e8bb0c7a&3rd=MzA3MDU4NTYzMw==&scene=6#rd'
    #url = 'http://mp.weixin.qq.com/s?__biz=MjM5ODExMjg0MQ==&mid=203299354&idx=3&sn=9e5306ac080e55dbc8095237f61cb524&3rd=MzA3MDU4NTYzMw==&scene=6#rd'
    data = {
            'type': u'元搜索',
            'origin_source': u'微信搜索',
            'key': 'aaaaaa',
            'source_type': u'事件',
        }
    key = u'武汉获评全国文明城市'
    KeywordsCrawler(key=key,data=data).crawl()
    # ContentCrawler(key=url, data=data).crawl()
    # FirstCrawler.init()
    FirstCrawler(key=u'oIWsFt2sFmMXiDf2BGLZYZ0LDcJ4').crawl()

    # global listips
    # listips = getIP(10)
    # url = 'http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid=oIWsFt2sFmMXiDf2BGLZYZ0LDcJ4'
    # get_SNUID(url)
    print '==='

    # from urllib import quote, unquote
    # url = 'http://api.weibo.cn/2/profile?gsid=4uPi47123o3ExB67Ymgsu9t9la1&wm=3333_2001&i=27bd163&b=1&from=1051293010&c=iphone&v_p=18&skin=default&v_f=1&s=d2672a12&lang=zh_CN&ua=iPhone7,2__weibo__5.1.2__iphone__os8.1.3&luicode=10000194&uid=3906197901&nick=%E5%8C%97%E4%BA%AC%E8%B4%A8%E7%9B%91&uicode=10000198'
    # print unquote(str(url))
