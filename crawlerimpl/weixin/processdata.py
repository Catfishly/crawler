#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import requests
import datetime
import json
#from datetime import datetime
import time
from bs4 import BeautifulSoup
from lxml import etree

def get_urls_re(homepage, time = 10, cookie=''):

    html_stream = None
    count = 0
    while count < 2:
        try:
            html_stream = requests.get(homepage ,cookies=cookie ,\
                timeout = time)
        except:
            count += 1
        else:
            break
    return html_stream

def _wrap(lit):
    if isinstance(lit, list):
        return list(lit)
    else:
        return None

def extract_key(text):
    if not text:
        return ""
    if not isinstance(text, unicode):
        text = unicode(text, 'utf8')
        
    chinese_symbols = u"[“”‘’！？—…。，·：、￥（）【】《》〖〗]"
    en_symbols = r"[`~!@#\$%\^&\*\(\)_\+=\-\{\}\[\];:\",\.<>/\?\\|' + \"\']"
    text = re.sub(chinese_symbols, ' ', text)
    text = re.sub(en_symbols, ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip().lower()

def clear_space(text):
    text = unicode(text) if type(text) == str else text
    assert isinstance(text,unicode)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace(' ', '')
    text = text.replace(ur'　','')
    text = text.replace(ur' ', '')
    return text

def clear_label(text, root=''):

    assert isinstance(text,list)
    content = ''
    for item in text:
        item = unicode(item)
        str_comp = r"(?<=class=\").+?(?=\")|(?<=id=\").+?(?=\")|<script>.+?</script>"
    #    str_comp = r"(?<=class=\").+?(?=\")|(?<=id=\").+?(?=\")"
        strinfo = re.compile(str_comp, re.DOTALL)
        item = strinfo.sub('',item)
        imginfo = re.compile(r'\S*?src',re.I)
        item = imginfo.sub('src',item)
        if root:
            img_list=re.findall(r"(?<=src=\").+?(?=\")|(?<=src=\').+?(?=\')|(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,item)
            for img in img_list:
                new_img = ''
                if img.find('http') == -1:
                    new_img = HandleUrl.join_url_path(root,img)
                    item = item.replace(img, new_img)
                else:
                    pass
        content += item
    return content

def change_to_json(text):

    assert isinstance(text,str)
    try:
        jsons = json.loads(text)
    except:
        jsons = {}
    return jsons

def utc2local(utc_st):
    assert isinstance(local_st, datetime.datetime)
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st

def local2utc(local_st):
    assert isinstance(local_st, datetime.datetime)
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st

def new_time():
    date = {}
    date = {
     'crtime_int': int(time.time() * 1000000),
     'crtime': datetime.datetime.now()
    }
    return date

def get_charset(html):
    try:
        soup = BeautifulSoup(html[html.find(">")+1:])
    except:
        return 'utf-8'
    tags = soup.find_all(re.compile(r'meta', re.I))
    for tag in tags:
        if tag.get('content'):
            match = re.search(r'charset=(.*)',tag['content'])
            if match:
                coding = match.group(1)
                return coding
    return 'utf-8'

def getIP(size):
    ips = {}
    url = "http://www.kjson.com/proxy/search/1/?sort=down&by=asc&t=highavailable"
    html_stream = requests.get(url, timeout=5)
    html = etree.HTML(html_stream.text)
    content = "//table[@id='proxy_table']/tr"
    iplist = html.xpath(content)
    for ipitem in iplist:
        status = ipitem.xpath("td[@class='enport']/text()")
        prot = "0"
        if status != None and status != [] and status[0] == "DCA":
            prot = "80"
            type = ipitem.xpath("td[3]/text()")
            if type[0] == "HTTP":
                ip = ipitem.xpath("td[1]/text()")
                tmplist = {"http://" + ip[0] + ":" + prot: "http"}
                ips.update(tmplist)
    return ips

class HandleContent(object): 

    def __init__(self):
       pass

    @staticmethod  
    def get_BScontext(html ,text=False):
        try:
            soup = BeautifulSoup(html) if text else BeautifulSoup(html.text)
        except:
            soup = ''
        return soup

    @staticmethod
    def get_context(html ,xpath):
        text = ''
        tree = etree.HTML(html.text)
        dom = tree.xpath(xpath)
        for item in dom:
            if item.strip() == '':
                continue
            else:
                text +=' ' + item.strip()
        return text.strip()

    @staticmethod
    def get_title(html ,xpath=''):
        title = HandleContent.get_context(html,xpath)
        if title.strip() == '':    
            soup = HandleContent.get_BScontext(html)
            title = soup.title.string if soup.title else ''
          
        return title
    @staticmethod
    def strformat(time_str):
        time_str = time_str.strip()
        time_format = ''
        if time_str.find('/') >0:
            if time_str.find(':') >0:
                time_format = "%Y/%m/%d %H:%M:%S"
            else:
                time_format = "%Y/%m/%d"
        elif time_str.find(':') == -1:
            time_format = "%Y-%m-%d"
        elif time_str.count(':') ==1:
            time_format = "%Y-%m-%d %H:%M"
        elif time_str.count(':') == 2 and time_str.find('+') >0:
            time_format = "%a %b %d %H:%M:%S %Y"
            time_str = time_str.replace(' +0800','')
        else:
            time_format = "%Y-%m-%d %H:%M:%S"
        try:
            pub_time = datetime.datetime.strptime(time_str, time_format)
        except:
            pub_time = ''
        return pub_time

    @staticmethod
    def get_pubtime(html ,xpath='', time_format='', match_str=''):
        text = HandleContent.get_context(html,xpath)
        if text.strip() == '':
            pub_time = HandleContent.find_pubtime(html.text)
        elif match_str:
            match = re.search(match_str, text)
            date_format = time_format if time_format else HandleContent.get_time_format(match)
            pub_time = datetime.datetime.strptime(text, date_format)
        else:
            pub_time = HandleContent.find_pubtime(text)
        pub_time = local2utc(pub_time) if pub_time else datetime.datetime.utcfromtimestamp(0)
        nowyear = datetime.datetime.now().year
        pubyear = pub_time.year
        if pubyear > nowyear:
            pub_time = pub_time.replace(nowyear)
        return pub_time

    @staticmethod
    def get_author(html ,xpath=''):
        author = HandleContent.get_context(html,xpath)
        return author

    @staticmethod
    def find_pubtime(text):
        #匹配标准时间  2014-09-18 18:12:20 ((日期|时间)) 
        match_str_1 = u'(日期|时间)：\s*(\d{4}-\d{1,2}-\d{1,2}\s*(?:\d{1,2}:\d{1,2}:\d{1,2})?)'
        match_ls = [match_str_1]
        for match_str in match_ls:
            match = re.search(match_str, text)
            if match:
                return HandleContent.strformat(match.group(2))
       #匹配： 2014-07-02 11:03:44
        match =re.search('\s*(\d{4}-\d+-\d+\s\d{1,2}:\d{1,2}:\d{1,2})',text)
        if match:
            return HandleContent.strformat(match.group(1))
       #2013/11/11 11:13:22
        match =re.search('\s*(\d{4}/\d+/\d+\s\d{1,2}:\d{1,2}:\d{1,2})',text)
        if match:
            return HandleContent.strformat(match.group(1))
         #消息来源： 发布日期：2014-05-05
        match = re.search(u'(日期|时间)：\s*(\d{4}-\d{1,2}-\d{1,2})',text)
        if match:
            return HandleContent.strformat(match.group(2))
        #发表时间：2014/7/8
        match = re.search(u'(日期|时间)(\|)?(：|:)(&nbsp;)*?\s*(\d{4}/\d{1,2}/\d{1,2})',text)
        if match:
            return HandleContent.strformat(match.group(5))
        #匹配时间为【发布时间】
        match = re.search(u'发[布表](时间|日期)】(.|\n)+\s*(\d{4})年(\d{1,2})月(\d{1,2})日',text)
        if match:
            year = int(match.group(3))
            month = int(match.group(4))
            day = int(match.group(5))
            return datetime.datetime(year, month, day)
        #匹配汉字时间  2014年03月02日
        match = re.search(u'发[布表](时间|日期)：\s*(\d{4})年(\d{1,2})月(\d{1,2})日',text)
        if match:
            year = int(match.group(2))
            month = int(match.group(3))
            day = int(match.group(4))
            return datetime.datetime(year, month, day)
        #匹配时间为2014年03月20日 15:01
        match = re.search(u'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2}):(\d{1,2})',text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            hour = int(match.group(4))
            minute =  int(match.group(5))
            return datetime.datetime(year, month, day,hour,minute,0)
        #匹配汉字 日期：2014-06-05
        match = re.search(u'\s*(\d{4}-\d{1,2}-\d{1,2})', text)
        if match:
            return HandleContent.strformat(match.group(1))
        match = re.search(u'时间(：|:)\s*(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year = int(match.group(2))
            month = int(match.group(3))
            day = int(match.group(4))
            return datetime.datetime(year, month, day)
        #匹配汉字时间 日期：2009年10月02日
        match = re.search(u'日期：\s*(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return datetime.datetime(year, month, day)
        #匹配时间格式为时间: 2012.09.20
        match = re.search(u'(日期|时间):\s*(\d{4})\.(\d{1,2})\.(\d{1,2})', text)
        if match:
            year = int(match.group(2))
            month = int(match.group(3))
            day = int(match.group(4))
            return datetime.datetime(year, month, day)
        #匹配格式为 2014-02-09 09:9                 2014-05-06 16:21
        match =re.search('\s*(\d{4}-\d{2}-\d+\s\d{1,2}:\d{1,2})',text)
        if match:
            return HandleContent.strformat((match.group(1)))
        return None



class HandleUrl(object):

    def __init__(self):
       pass

    @staticmethod
    def join_url_path(root, path):
        path = path.strip()
        path.replace('','.')
        ls = root.split('/')
        root = ls[0] + '//' + ls[1] + ls[2]
        match = re.search(r'.*?(\w.+$)',path)
        if match:
            path=match.group(1)
        return root + '/' +path

    @staticmethod
    def get_url(data):
        link_list=re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,data)
        return _wrap(link_list)

    @staticmethod
    def judge_url(url):
        url_res = ''
        if url.find('javascript') >= 0:
            return url_res
        elif url.find('http://mp.weixin.qq.com/') == -1:
            return url_res
        else:
            url_res = url.strip()
        return url_res
