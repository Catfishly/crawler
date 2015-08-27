# -*- coding: utf-8 -*-

import logging
import json
import time
from datetime import timedelta
import datetime
import requests
import re
import time
import random
import socket



logger = logging.getLogger("ecommercecrawler")

def clean_space(text):
    if not isinstance(text,unicode):
        text = unicode(text,'utf-8')
    return "".join(text.split(' '))

def extract_text(text):
    if not isinstance(text,unicode):
        text = unicode(text,'utf-8')
    chinese_symbols = u"[“”‘’！？…。]"
    en_symbols = r"[`~!@#\$%\^&\*\(\)_\+=\{\}\[\];\",<>/\?\\|' + \"\']"
    text = re.sub(chinese_symbols, ' ', text)
    text = re.sub(en_symbols, ' ', text)
    return text

def extract_title(text):
    if not isinstance(text,unicode):
        text = unicode(text,'utf-8')
    chinese_symbols = u"[“”‘’！？—…。，·：、（）【】《》〖〗]"
    en_symbols = r"[`~!@#\$%\^&\*\(\)_\+=\-\{\}\[\];:\",\.<>/\?\\|' + \"\']+"
    text = re.sub(chinese_symbols, ' ', text)
    text = re.sub(en_symbols, ' ', text)
    text = text.strip()
    return text

def extract_category(self):
  
    priorcategory = self.data['priorcategory']
    presentcategory = self.data['presentcategory']
    # presentcategory = priorcategory
    if len(presentcategory) != 3:
        print 'error :The incomplete presentcategory'
        logger.error('error :The incomplete presentcategorys ')
        one=two=three = ''
    else:
        one = presentcategory[0]
        two = presentcategory[1]
        three  = presentcategory[2]
    if len(priorcategory) !=3:
        mappriorcategory = {}
        print 'error :The incomplete priorcategory'
        logger.error('error :The incomplete priorcategory')
    else:
        mappriorcategory = {
            'first':priorcategory[0],
            'secod':priorcategory[1],
            'thrid':priorcategory[2]
        }
    category_data = {
        # 'history_price': {'a': 1},
        'first_level':one,
        'second_level':two,
        'third_level':three,
        'source_level':mappriorcategory,
    }
    return category_data

class ProcessData():

    @staticmethod
    def str_datetime(str_time):
        str_time = str_time.strip()
        if str_time.count(':')==2:
            time_format = '%Y-%m-%d %H:%M:%S'
        elif str_time.count(':')==1:
            time_format = '%Y-%m-%d %H:%M'
        elif str_time.count('-') == 2:
            time_format = '%Y-%m-%d'
        try:
            times = datetime.datetime.strptime(str_time,time_format) - timedelta(hours = 8)
        except:
            times = datetime.datetime.strptime("1900-01-01",'%Y-%m-%d')
        return times

    @staticmethod
    def get_web_data(url):
        count = 0
        while count < 2:
            try:
                html_stream = requests.get(url, timeout = 5)
            except requests.exceptions.Timeout:
                time.sleep(random.randint(1,5))
                count += 1
            except socket.timeout:
                time.sleep(random.randint(1,8))
                count += 1                
            except URLError, e:
                logger.error(url)
                return {}
            except Exception,e:
                logger.error(e)
                logger.error(url)
                return {}
            else:
                count = 2
                break
        if count != 2:
            logger.error("timeout: %s"%url)
        return html_stream

    @staticmethod
    def get_json_data(url,**keys):
        count = 0
        while count < 2:
            try :
                html_stream = requests.get(url ,params = keys.get('parameter',{}),timeout = 3)
            except requests.exceptions.Timeout:
                time.sleep(random.randint(1,5))
                count += 1
            except socket.timeout:
                time.sleep(random.randint(1,8))
                count += 1
            except Exception,e:
                logger.error(e)
                logger.error(url)
                return {}
            else:
                count = 2
                break
        if count != 2:
            logger.error("timeout: %s"%url)
        try:
            jsons = json.loads(html_stream.text)
        except:
            jsons = {}

        return jsons

if __name__ == "__main__":
    url = 'http://mobile.gome.com.cn/mobile/product/search/keywordsSearch.jsp?\
          body=%7B%22searchType%22%3A%20%220%22%2C%20%22catId%22%3A%20%22cat10000230\
          %22%2C%20%22regionID%22%3A%20%2211010200%22%2C%20%22sortBy%22%3A%20%227%22%\
          2C%20%22currentPage%22%3A%20234%2C%20%22pageSize%22%3A%2010%7D'

    ProcessData.get_json_data(url)