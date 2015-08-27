#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
root_mod = '/home/xxguo/Project/crawler'
sys.path.append(root_mod)
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce.model import EcBasicModel,\
    EcDetailModel, EcCommentModel 
from processdata import ProcessData,\
    extract_title, extract_category, extract_text

class FirstCrawler(Crawler):
    type = "ecommerce.yhd.firstlvl"

    @staticmethod
    def init(conf=None):
        pass
   #     Scheduler.schedule(FirstCrawler.type, interval=86400)

    def crawl(self):
        url = "http://interface.m.yhd.com/ \
               mcategory/servlet/CentralMobileFacadeJsonServlet/ \
               getNavCategoryWithKeywordByRootCategoryId? \
               rootCategoryId=0&categoryNavId=0&provinceId=1"
        try:
            jsons = ProcessData.get_json_data(url.replace(' ',''))
            data = jsons['data']
        except Exception,e:
            self.logger.error(url)
            self.logger.error(e)            
            print 'error ',url
        for item in data:
            categoryName1 = item['categoryName']
            for child in item['childCategoryVOList']:
                if not child.has_key('boundCategoryId'):continue
                priorcategory = []
                categoryName2 = child['categoryName']
                priorcategory.extend([categoryName1,categoryName2])
                self.handle(child['id'],priorcategory)

    def handle(self,id,priorcategory):
        data = {
            'priorcategory':priorcategory
        }
    
        Scheduler.schedule(ThirdCrawler.type, key=id, data=data)
       

class ThirdCrawler(Crawler):
    type = "ecommerce.yhd.thirdlvl"

    def crawl(self):
        cid = str(self.key)
        categorys = self.data['priorcategory']
        url = "http://interface.m.yhd.com/\
               mcategory/servlet/CentralMobileFacadeJsonServlet/\
               getNavCategoryWithKeywordByRootCategoryId?rootCategoryId=\
               %s&categoryNavId=0&provinceId=1" %(cid)
        try:
            jsons = ProcessData.get_json_data(url.replace(' ',''))
            data = jsons['data']
        except Exception,e:
            self.logger.error(url)
            self.logger.error(e)
            print 'error ',url
        for item in data:
            priorcategory = []
            priorcategory.extend(categorys)
            priorcategory.append(item['categoryName'])            
            if item.has_key('boundCategoryId'):
                keys = item['boundCategoryId']
            else:
                keys = item['linkUrl']
            data = {
                'priorcategory':priorcategory,
#                'presentcategory':presentcategory
            }   

            Scheduler.schedule(ListCrawler.type, key=keys, data=data)


class ListCrawler(Crawler):
    type = "ecommerce.yhd.goodslist"
    
    def product_list_xpath(self,xpath):

        data = {
            'list': "//div[@class='mod_product_list clearfix']/div[@class='list_width clearfix']/\
                     div[@class='mod_search_pro']",
            'adword': "div[@class='itemBox']/p[@class='storeName']/a/text()",
            'title': "div[@class='itemBox']/p[@class='proName']/a/text()",
            'price': "div[@class='itemBox']/p[@class='proPrice']/em/@yhdprice",
            'original_price': "div[@class='itemBox']/p[@class='proPrice']/em/del/text()",
            'source_id': "div[@class='itemBox']/p[@class='proPrice']/em/@productid",
            'score': "div[@class='itemBox']/p[@class='proPrice']/span[@class='positiveRatio']/text()"
        }
        return data.get(xpath,'')

    def search_list_xpath(self,xpath):

        data = {
            'list': "//div[@class='layout_search_main']/div[@data-tpa='SEARCH_MAIN_LIST']/\
                     div[@class = 'mod_search_list mod_search_list_zhai ']/\
                     ul[@class='clearfix']/li[@class='search_item']",
            'title': "div[@class='search_item_box']/p[@class='title']/a[@class='title']/text()",
            'adword': "div[@class='search_item_box']/div[@class='item_promotion_text']/\
                       div[@class='tip']/text()",
            'price': "div[@class='search_item_box']/div[@class='pricebox clearfix']/\
                      span[@class='color_red price']/@yhdprice",
            'source_id': "div[@class='search_item_box']/div[@class='pricebox clearfix']/\
                          span[@class='color_red price']/@productid",
            'score': "div[@class='search_item_box']/p[@class='comment']/span/text()"
        }
        return data.get(xpath,'""')
    def mackining(self,name):
        data = ''
        for item in name:
            data += item.strip()
        return data

    def get_url(self,key,pages):
        pages = 5
        base_url = "http://list.yhd.com/c%s-0-0"
        RUMP = "#page=%s&sort=1"%pages
        if key.find('http:') >=0 :
            url = key + RUMP
        else:
            url = base_url + RUMP
        return url

    def crawler_data(self,tree):
        category_data = extract_category(self)

        XPATH = self.search_list_xpath
        if len(tree.xpath(XPATH('list'))) == 0:
            XPATH = self.product_list_xpath
        dom = tree.xpath(XPATH('list'))
        for item in dom:
            crawl_data = {}
            craw = [
                'title','adword',
                'price','original_price',
                'source_id','score',
            ]

            for value in craw: 
                crawl_data[value] = self.mackining(item.xpath(XPATH(value)))
            crawl_data['price'] = float(crawl_data['price'])
            try:
                f = lambda x: int(x[:-1])/100.00
                crawl_data['score'] = float(f(crawl_data['score']))
            except:
                crawl_data['score'] = 0
            crawl_data.update(category_data)
            crawl_data['source'] = 'yhd'
            model = EcBasicModel(crawl_data)
            export(model)
            data = {
                'priorcategory': self.data['priorcategory'],
                'presentcategory': self.data['priorcategory']           
            }            
            data["uuid"] = model["id"]
            Scheduler.schedule(DetailCrawler.type, key=str(self.key), data=data)

    def crawl(self): 
        key = str(self.key)
        count = 2 #页数初始值为3
        pages = 1 #从第一页开始
        for i in xrange(1,count):
            url = self.get_url(key,pages)
            html_stream = ProcessData.get_web_data(url)
      #      print html_stream.text.encode('utf-8')
            tree = etree.HTML(html_stream.text)
            self.crawler_data(tree)
 

class DetailCrawler(Crawler):

    type = "ecommerce.yhd.goodsdetail"
    def crawl(self):

        wareId = str(self.key)
        url = "http://item.yhd.com/item/%s"%wareId
        html_stream = ProcessData.get_web_data(url)
  #      print html_stream.text.encode('utf-8')
        tree = etree.HTML(html_stream.text)
        self.crawler_data(tree)

    def crawler_data(self,tree):
        ids =  self.data.get('uuid')
        category_data = extract_category(self)
        introduce = tree.xpath(self.ware_xpath('introduce'))
        specifications = tree.xpath(self.ware_xpath('specifications'))
        introd = {}
        ecnorms = {}
        for item in introduce:
            item = item.strip()
            if item == '': continue
            item = item.split(u'：',1)
            try:
                introd[item[0]] = item[1]
            except:
                pass
        for item in specifications:
            label = item.xpath(self.ware_xpath('label'))
            names = []
            values = []
            for i in label:
                i = i.strip()
                if i.strip() == '':  continue
                names.append(i)
            dd = item.xpath(self.ware_xpath('item'))
            for i in dd:
                i = i.strip()
                if i.strip() == '':  continue        
                values.append(i)
            ecnorms.update(map(lambda x,y:[x,y],names,values))

        crawl_data = {
            'id': ids,
            'source': self.data.get('source'),
            'source_id': str(self.key),
            'summary': ecnorms,
            'introduce': introd,
            'version': ecnorms.get(u'型号',''),
            'brand': ecnorms.get(u'商品品牌','')
        }
        crawl_data.update(category_data)
        model = EcDetailModel(crawl_data)
        export(model)

    def ware_xpath(self,xpath):
        data = {
            'introduce': "//dl[@class='des_info clearfix']/dd/text()",
            'specifications': "//div[@tabindex='1']/dl[@class='standard']",
            'item': "dd/text()",
            'label': "dd/label/text()"
        }
        return data.get(xpath,'""')


if __name__ == "__main__":
    data = {
        'source': 'yhd',
        "priorcategory" : ["冰箱 洗衣机 空调","冰箱/冷柜","冰箱"],
        "presentcategory": ["冰箱 洗衣机 空调","冰箱/冷柜","冰箱"],
        # 'uuid':uuid.uuid1()
        }    
  #  keys = 'http://list.yhd.com/c23021-0-0/'
 #   keys = 'http://list.yhd.com/c21307-0-0/'
    keys = 'http://list.yhd.com/c32159-0-0/'
    ListCrawler(key =keys,data=data).crawl()
 #   DetailCrawler(key ='19010979',data=data).crawl()
    # f = FirstCrawler()
    # f.crawler()