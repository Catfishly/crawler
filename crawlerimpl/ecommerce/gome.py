# -*- coding: utf-8 -*-
import sys
# root_mod = '/home/liyang/Documents/shendu-ecommerce-crawler'
# root_mod = '/home/xxguo/Project/crawler'
# sys.path.append(root_mod)

import requests
import json
import pymongo
from urllib import quote,unquote
import uuid
import datetime
from datetime import timedelta
#import lxml.html.soupparser as soupparser
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce.model import EcBasicModel,\
    EcDetailModel, EcCommentModel 
from processdata import ProcessData,\
    extract_title, extract_category, extract_text

class FirstCrawler(Crawler):
    type = "ecommerce.gome.firstlvl"
    
    @staticmethod
    def init(conf=None):
        pass
  #      Scheduler.schedule(FirstCrawler.type, interval=86400)

    def crawl(self):
        url = "http://mobile.gome.com.cn/mobile/product/allCategorys.jsp"
        jsons = ProcessData.get_json_data(url)
        if jsons == {}:
            return {} 
        category1 = jsons['firstLevelCategories']
        for first_item in category1:
            name1 = first_item['goodsTypeName']   #1 lev name
            try :
                category2 = first_item['goodsTypeList']
            except:
                pass
            for second_item in category2:
                name2 = second_item['goodsTypeName']
                #print name
                try :
                    category3 = second_item['goodsTypeList']
                except:
                    pass
                for third_item in category3:
                    try: 
                        third_id = third_item['goodsTypeId']
                        name3 = third_item['goodsTypeLongName']
                    except:
                        pass
                    # print third_id
                    # print name3.encode('utf-8')
                    priorcategory = []
                    priorcategory.append(name1)
                    priorcategory.append(name2)
                    priorcategory.append(name3)
                    #presentcategory = priorcategory
                    data = {
                        'priorcategory': priorcategory
                        #'presentcategory':presentcategory
                        }
                    Scheduler.schedule(ListCrawler.type, key=third_id, data=data)


class ListCrawler(Crawler):
    type = "ecommerce.gome.goodslist"   
    def get_url(self,catId,currentPage):
        front = "http://mobile.gome.com.cn/mobile/product/search/keywordsSearch.jsp?body="
        body = {
            "pageSize":10,
            "searchType":"0",
            "sortBy":"7",
            "regionID":"11010200"}
        body['catId'] = catId
        body['currentPage'] = currentPage
        url = front + quote(str(body).replace("\'","\""))
        return url
    def get_page(self,catId):
        json =ProcessData.get_json_data(self.get_url(catId,1))
        try:
            totalpage = json['totalPage']
        except Exception,e:
            self.logger.error(e)
            print "totalPage fail!"
            return 0
        return totalpage
    def crawl(self):
        catId = str(self.key)
        category_data = extract_category(self)  
        totalpage = self.get_page(catId)
        if totalpage == 0:
            return {}
        for i in range(1,totalpage+1):
            url = self.get_url(catId,i)
            jsons = ProcessData.get_json_data(url)
            try:
                goodsList = jsons['goodsList']
            except Exception,e:
                self.logger.error(url)
                self.logger.error(e)
                print "get goodsList fail"
            for j in range(len(goodsList)):
                goods = goodsList[j]
                goodsName = goods['goodsName']
                goodsNo = goods['goodsNo']
                skuID = goods['skuID']
                # print goodsNo
                # print skuID
                crawl_data = {
                    # 'id': uuid.uuid1(),
                    'source_id': goodsNo,
                    'source': self.data.get('source'),
                    'title': goods['goodsName'],
                    'adword': goods['ad'],
                    'price': float(goods['lowestSalePrice']),
                    'original_price': float(goods['highestSalePrice']),
                    #'score': ecsumscores
                    }
                crawl_data.update(category_data)
                model = EcBasicModel(crawl_data)
                export(model)
                data = {
                    'priorcategory': self.data['priorcategory'],
                    'presentcategory': self.data['priorcategory']
                    }
                data["uuid"] = model["id"]
                Scheduler.schedule(DetailCrawler.type, key=goodsNo, data=data)
                Scheduler.schedule(CommentCrawler.type, key=goodsNo, data=data)

class CommentCrawler(Crawler):
    type = "ecommerce.gome.goodscomment"

    def get_url(self,goodsNo,currentPage):
        front = "http://mobile.gome.com.cn/mobile/product/goodsAppraise.jsp?body="
        body = {
            "appraiseType":"0",
            "pageSize":"10"
            }
        body["goodsNo"] = goodsNo
        body["currentPage"] = currentPage
        url = front + quote(str(body).replace("\'","\""))
        return url 
    def get_page(self,goodsNo):
        json = ProcessData.get_json_data(self.get_url(goodsNo,1))
        try:
            totalnum = int(json['appraiseNumArray'][0])
        except Exception,e:
            self.logger.error(e)
            print "totalPage fail!"
            return 0
        totalpage = int(totalnum/10)
        return totalpage
    def crawl(self):
        ecid =  self.data['uuid']
        goodsNo = str(self.key)
        category_data = extract_category(self)
        totalpage = int(self.get_page(goodsNo))    
        if totalpage == 0:
            print "get_page fail"
            return {}
        for i in range(totalpage):
            url = self.get_url(goodsNo,i)
            json = ProcessData.get_json_data(url)
            try:
                appraise = json['appraiseArray']
            except Exception,e:
                self.logger.error(url)
                self.logger.error(e)
                print "get appraise fail"
            for item in appraise:
                commentid = item['id']
                summary = item['summary']
                score = item['appraiseGrade']
                userorderid = item['appraiseName']
                commenttime = ProcessData.str_datetime(item['appraiseTime'])
                # print commentid
                # print summary.encode('utf-8')
                comment_data={
                    'ecid': ecid,        #commodity table foreign key
                    'source_id': goodsNo,
                    'source': self.data.get('source'),
                    'comment_id': item['id'],  #review id
                    'score': item['appraiseGrade'],         #commodity score
                    'pubtime': ProcessData.str_datetime(item['appraiseTime']),
                    'user_id': item['appraiseName'],
                    'content': item['summary']
                }
                comment_data.update(category_data)
                model = EcCommentModel(comment_data)
                export(model)

class DetailCrawler(Crawler):
    type = "ecommerce.gome.goodsdetail"
    def get_basic_url(self,goodsNo):
        front = "http://mobile.gome.com.cn/mobile/product/productShow.jsp?body="
        body = {"skuID":"1119570510"}
        body['goodsNo'] = goodsNo
        url = front + quote(str(body).replace("\'","\""))
        return url 
    def get_detail_url(self,goodsNo):
        url = "http://m.gome.com.cn/product_des-%s-.html?from=cat10000" %(goodsNo)
        return url 
    def crawl(self):
        skulist = []
        goodsNo = str(self.key)
        ids =  self.data.get('uuid')
        category_data = extract_category(self)
        url = self.get_detail_url(goodsNo)
        html = ProcessData.get_web_data(url)
        tree = etree.HTML(html.text)
        r = tree.xpath("//div[@class='wap_tab_con']/div[2]/table[@class='parameter']/tbody/tr")
        i = len(r)
        standard = {}
        r1 = tree.xpath("//table[@class='parameter']/tbody/tr")
        for x in r1:
            m1 = x.xpath("td[@class='bg']")
            m2 = x.xpath("td[@class='bgv']")
            if len(m1) != 0 and len(m2) != 0 :
                standard[m1[0].text] = m2[0].text
        rpack = tree.xpath("//div[@class='wap_tab_con']/div[3]")
        ecparkinglist = rpack[0].text
        rafter = tree.xpath("//div[@class='wap_tab_con']/div[4]")
        ecaftersale = rafter[0].text
        ecbrands = standard[u'品牌'] if standard.get(u'品牌') else ''
        # for k,v in standard.items():
        #     print k.encode('utf-8'),v.encode('utf-8')
        # print ecbrands.encode('utf-8')
        json = ProcessData.get_json_data(self.get_basic_url(goodsNo))
        skulist = json['skuList']
        for sku in skulist:
            ecnowprice = sku['skuPrice']
            ecnmaket = sku['skuPriceDesc']
            ecname = sku['skuName']
            adword = sku['promWords']
            skuid = sku['skuID']
            ecimglist = sku['skuSourceImgUrl']
            source_id = goodsNo+'-'+skuid
            crawl_data = {
            'id': ids,
            'source': self.data.get('source'),
            'source_id': source_id,
            'summary': standard,
            'introduce': {},
            'name': ecname,
            'brand': ecbrands
            }
            crawl_data.update(category_data)
            model = EcDetailModel(crawl_data)
            export(model)




if __name__ == "__main__1":
    test = GOMEHandler()
    test = FirstCategory()
    #test.wareComment()
    #test.wareInformation()

if __name__ == "__main__":
    # data = {
    #     'source': 'gome',
    #     "priorcategory" : ["冰箱 洗衣机 空调","冰箱/冷柜","冰箱"],
    #     "presentcategory": ["冰箱 洗衣机 空调","冰箱/冷柜","冰箱"],
    #     'uuid':uuid.uuid1()
    #     }
    # data = {'source':'gome'}
    FirstCrawler(data={'source':'gome'}).crawl()
    # DetailCrawler(key='9133023740',data = data).crawl()
    # CommentCrawler(key='9133023740',data = data).crawl()
    # ListCrawler(key='cat10000054',data = data).crawl()

