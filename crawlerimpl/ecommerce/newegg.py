#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
import sys

root_mod = '/home/xxguo/Project/shendu-ecommerce-crawler'
sys.path.append(root_mod)

import pymongo
import math
import uuid
from urllib import quote,unquote
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce.model import EcBasicModel,EcDetailModel,EcCommentModel
from processdata import ProcessData,extract_title,extract_category,extract_text

class FirstCrawler(Crawler):
    type = "ecommerce.newegg.firstlvl"

    def crawl(self):
        url = 'http://www.ows.newegg.com.cn/category.egg'
        try:
            jsons = ProcessData.get_json_data(url)
        except:
            print 'error ',url
            return
        for item1 in jsons:
            CatName1 = item1['CatName']
            for item2 in item1['SubCategories']:
                CatName2 = item2['CatName']
                for item3 in item2['SubCategories'] :
                    priorcategory = []
                    priorcategory.extend([CatName1,CatName2,item3['CatName']])
                    self.handle(item3['CatID'],priorcategory)
                          
       
    def handle(self,CatID,priorcategory):
        data = {
            'priorcategory':priorcategory
        }
        Scheduler.schedule(ListCrawler.type, key=CatID, data=data)


class ListCrawler(Crawler):
    type = "ecommerce.newegg.goodslist"

    def get_data(self,CatID,pages):
        url = 'http://www.ows.newegg.com.cn/cat/%s'%(str(CatID))
        list_urls = {
            'page': str(pages),
            'pagesize': 20,
            'sort': 10
            }
        return ProcessData.get_json_data(url,parameter=list_urls)

        
    def crawl(self):

        CatID = self.key
#        category_data = extract_category(self)

        pages = 1
        count = True
        while True:
            try:
                jsons = self.get_data(CatID,pages)
                if pages==1 : count = math.ceil(int(jsons['PageInfo']['TotalCount'])/100)
                print count 
                break
                lists = jsons['wareInfo']
            except:
                print 'error url , CatID = %s,pages = %s'%(CatID,pages)
                return
        

if __name__ == "__main__":
    # f = DetailCrawler()
    # f.crawl()
    data = {'source': 'newegg'}
    FirstCrawler(key='2405',data=data).crawl()    
