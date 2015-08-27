#!/usr/bin/python
#coding: utf-8

import datetime
import pymongo
import sys
import re
import requests
from lxml import etree
import codecs
from bs4 import BeautifulSoup
from get_stitle import gettitles
from get_spublish_time import getpublish_time

def str2datetime(time_str):
    #匹配的time_str，会有空格，导致后面strptime出错
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
    else:
        time_format = "%Y-%m-%d %H:%M:%S"
    try:
        pub_time = datetime.datetime.strptime(time_str, time_format)
    except:
        pub_time = ''
    return pub_time

def get_publish_times(html):
    xpath = getpublish_time(html)
    if xpath == '':
        return get_publish_time(html.text)
    if html.text =='' or html.text == None:
        return get_publish_time(html.text)
    try:
        tree = etree.HTML(html.text)
        if tree == None or tree == '':
            return get_publish_time(html.text)
        dom = tree.xpath(xpath)
    except:
        dom = ''
    txt = ''
    for item in dom:
        txt +=item.strip()
#        break
    if txt=='':
       return  get_publish_time(html.text)
    elif re.match(ur'.*[\u4e00-\u9fa5]{1,}.*',txt):
        match = re.search('(\d{4}-\d{1,2}-\d{1,2})',txt)
        if match:
            return str2datetime(match.group(1))
        match = re.search(u'(\d{4})年(\d{1,2})月(\d{1,2})日', txt)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return datetime.datetime(year, month, day)
        return  get_publish_time(html.text)
    else:
        return str2datetime(txt)

def get_publish_time(text):
    #匹配标准时间  2014-09-18 18:12:20 ((日期|时间)) 
    match_str_1 = u'(日期|时间)：\s*(\d{4}-\d{1,2}-\d{1,2}\s*(?:\d{1,2}:\d{1,2}:\d{1,2})?)'
    match_ls = [match_str_1]
    for match_str in match_ls:
        match = re.search(match_str, text)
        if match:
            return str2datetime(match.group(2))
   #匹配： 2014-07-02 11:03:44
    match =re.search('\s*(\d{4}-\d+-\d+\s\d{1,2}:\d{1,2}:\d{1,2})',text)
    if match:
        return str2datetime(match.group(1))
   #2013/11/11 11:13:22
    match =re.search('\s*(\d{4}/\d+/\d+\s\d{1,2}:\d{1,2}:\d{1,2})',text)
    if match:
        return str2datetime(match.group(1))
     #消息来源： 发布日期：2014-05-05
    match = re.search(u'(日期|时间)：\s*(\d{4}-\d{1,2}-\d{1,2})',text)
    if match:
        return str2datetime(match.group(2))
    #发表时间：2014/7/8
    match = re.search(u'(日期|时间)(\|)?(：|:)(&nbsp;)*?\s*(\d{4}/\d{1,2}/\d{1,2})',text)
    if match:
        return str2datetime(match.group(5))
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
    match = re.search(u'(日期|时间|发布|表于):\s*(\d{4}-\d{1,2}-\d{1,2})', text)
    if match:
        return str2datetime(match.group(2))
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
        return str2datetime((match.group(1)))
    #上面没匹配到，找下面的
    return None
"""
    match = re.search('(\d{4}-\d{1,2}-\d{1,2})',text)
    if match:
        return str2datetime(match.group(1))
"""
    #若都没有匹配到，返回空
#根据tree正文提取

def get_titles(html):
    xpath = gettitles(html)
    if xpath == '':
        return get_title(html.text)
    if html.text ==''  or html.text == None:
        return get_title(html.text)
    try:
        global coding
        tree = etree.HTML(html.text)
        if tree == None or tree == '':
            return get_title(html.text)
        dom = tree.xpath(xpath)
    except:
        return get_title(html.text)
    txt = ''
    for item in dom:
        if re.search(r'^\|$',item.strip()):
            continue
        txt +=item.strip()
        if txt !='':
            break
    if txt=='':
       return  get_title(html.text)
    else:
        return txt

#根据title标签提取
def get_title(text):
    #beautifulsoup获取标签
    soup = BeautifulSoup(text[text.find(">")+1:])
    try:
        title = soup.title.string.strip() if soup.title else ''
    except AttributeError:
        title = ''
    
    #url = 'http://www.ls12365.gov.cn/www/zjgk/979.htm'
    #处理这个网站
    title = re.sub(u'^::', '', title)
    title = re.sub(u'::$', '', title)
    if title.find('_') >= 0:
        title = title.split('_',1)
        titles = re.search(u'\S+(市|省|州|区|质量|信息|技术|工商)\S*(网|局|网站)$',title[1])
        if titles:
            title = title[0].strip('_')
        else:
            title = title[1].strip('_')
    elif title.find('-') >=0:
        if re.search(ur'江门市质量技术监督局',title):
            return title.split('-')[1]
        title = title.split('-',1)
        if re.search(' Powered by',title[1]):
            return title[0]
        titles = re.search(u'\S+(市|省|州|区|质量|技术|信息|工商|金质|网站群)\S*(网|局|网站)$',title[1])
        if titles:
            title = title[0].strip('-')
        else:
            title = title[1].strip('-')
    elif title.find('|') >= 0:
        title = title.split('|',1)
        titles = re.search(u'\S+(市|省|州|区|质量|技术|工商)\S*(网|局|网站)$',title[1])
        if titles:
           title = title[0].strip('|')
        else:
           title = title[1].strip('|')
    elif title.find('>>') >=0:
        title =title.split('>>',1)
        titles = re.search(u'\S+(市|省|州|区|质量|技术|工商)\S*(网|局|网站)$',title[1])
        if titles:
            title = title[0].strip('>')
        else:
            title = title[1].strip('>')
    elif title.find(' ') >=0:
        title =title.split(' ',1)
        titles = re.search(u'\S+(市|省|州|区|质量|技术|信息|工商)\S*(网|局|网站)$',title[1])
        if titles:
            title = title[0].strip()
        else:
            title = title[1].strip()
    elif title.find(ur'－') >=0:
        title = title.split(ur'－',1)
        titles = re.search(u'\S+(市|省|州|区|工商|质量|技术|信息|金质)\S*(网|局|网站)$',title[1])
        if titles:
            title = title[0]
        else:
            title = title[1]

    return title
