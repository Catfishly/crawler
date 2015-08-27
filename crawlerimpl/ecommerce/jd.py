#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

import sys
root_mod = '/home/xxguo/Project/crawler'
sys.path.append(root_mod)

import pymongo
import math
import uuid
import re
from urllib import quote, unquote
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce.model import EcBasicModel,\
    EcDetailModel, EcCommentModel 
from processdata import ProcessData,\
    extract_title, extract_category, extract_text





class FirstCrawler(Crawler):
    type = "ecommerce.jd.firstlvl"

    @staticmethod
    def init(conf=None):
        pass
  #      Scheduler.schedule(FirstCrawler.type, interval=86400)

    def crawl(self):
        start_urls = "http://gw.m.360buy.com/client.action?functionId=catelogy&body="
        sencond_urls = {
            'catelogyId': '0',
            'isDescription': 'true',
            'isIcon': 'true',
            'level': '0'
        }

        url = start_urls + quote(str(sencond_urls))
        try:
            jsons = ProcessData.get_json_data(url)
            lists = jsons['catelogyList']
        except Exception,e:
            self.logger.error(url)
            self.logger.error(e)
            print 'error ',url
            return
        for i in range(len(lists)):

            cid = lists[i]['cid']
            priorcategory = []
#            presentcategory = []
            priorcategory.append(extract_title(lists[i]['name']))
            data = {
                'priorcategory':priorcategory,
#                'presentcategory':presentcategory
            }

            Scheduler.schedule(SecondCrawler.type, key=cid, data=data)


class SecondCrawler(Crawler):
    type = "ecommerce.jd.secondlvl"

    def crawl(self):

        # fid = '1620'
        # categorys = ["家居家装"]

        fid = self.key
        categorys = self.data['priorcategory']

        start_urls = "http://gw.m.360buy.com/client.action?functionId=catelogy&body="
        sencond_urls = {
            'catelogyId': str(fid),
            'isDescription': 'true',
            'isIcon': 'true',
            'level':'1'
        }
        url = start_urls + quote(str(sencond_urls))
        #print 'url ',url
        try:
            jsons = ProcessData.get_json_data(url)
            lists = jsons['catelogyList']
        except:
            print 'error ',url
            return
        if lists == []:
            return {}
        for i in range(len(lists)):

            cid = lists[i]['cid']
#            presentcategory = []
            priorcategory = []
            priorcategory.extend(categorys)
            priorcategory.append(extract_title(lists[i]['name']))
            data = {
                'priorcategory':priorcategory,
#                'presentcategory':presentcategory
            }
            Scheduler.schedule(ThirdCrawler.type, key=cid, data=data)



class ThirdCrawler(Crawler):
    type = "ecommerce.jd.thirdlvl"

    def crawl(self):
        fid = self.key
        categorys = self.data['priorcategory']
 #       fid = '1625'
 #       categorys = ["家居家装","清洁用品"]

        start_urls = "http://gw.m.360buy.com/client.action?functionId=catelogy&body="
        thrid_urls = {
            'catelogyId':str(fid),
            'isDescription':'false',
            'isIcon':'false',
            'level':'2'
        }
        url = start_urls + quote(str(thrid_urls))

        try:
            jsons = ProcessData.get_json_data(url)
            lists = jsons['catelogyList']
        except Exception,e:
            self.logger.error(url)
            self.logger.error(e)
            print 'error ',url
            return
        if lists == []:
            return {}
        for i in range(len(lists)):

            cid = lists[i]['cid']
#            presentcategory = []
            priorcategory = []
            priorcategory.extend(categorys)
            priorcategory.append(extract_title(lists[i]['name']))
            data = {
                'priorcategory':priorcategory,
#                'presentcategory':presentcategory
            }
            Scheduler.schedule(ListCrawler.type, key=cid, data=data)


class ListCrawler(Crawler):
    type = "ecommerce.jd.goodslist"


    def get_url(self,fid,pages):
        one_urls = "http://gw.m.360buy.com/client.action?functionId=searchCatelogy&body="
        list_urls = {
            'isLoadPromotion': 'true',
            'pagesize': '100',
            'isLoadAverageScore': 'true',
            'sort': '5',
            'page': str(pages),
            'userLocation': '114.40398301322374_30.452138106281158',
            'catelogyId': str(fid),
            'multi_suppliers': 'yes'
            }

        return one_urls + quote(str(list_urls))

    def crawl(self):
        # fid = '1662'
        # priorcategory = ["家居家装","清洁用品","衣物清洁"]
        # presentcategory = ['1','2','3']
        fid = self.key
        category_data = extract_category(self)

        count = 3 #页数初始值为3
        pages = 1 #从第一页开始

        while pages <= count:
            url = self.get_url(fid,pages)
            try:
                jsons = ProcessData.get_json_data(url)
                if pages==1 : count = math.ceil(int(jsons['wareCount'])/100)
                lists = jsons['wareInfo']
            except Exception,e:
                self.logger.error(url)
                self.logger.error(e)
                print 'error ',url
                return
            if lists == []:
                return {}
            for i in range(len(lists)):
                ids = uuid.uuid1() #cassandra 主键
                wareId = lists[i]['wareId']

                try:
                    f = lambda x: int(x[:-1])/100.00
                    ecsumscores = float(f(lists[i]['good'])) #商品总评分
                except:
                    ecsumscores = 0

                crawl_data = {
                    # 'id': uuid.uuid1(),
                    'source_id': wareId,
                    'source': self.data.get('source'),
                    'summary': {},
                    'title': lists[i]['wname'],
                    'adword': lists[i]['adword'],
                    'price': float(lists[i]['jdPrice']),
                    'original_price': float(lists[i]['martPrice']),
                    'score': ecsumscores
                }
                crawl_data.update(category_data)
                data = {
                    # 'uuid': ids,
                    'priorcategory': self.data['priorcategory'],
                    'presentcategory': self.data['priorcategory']
#                    'presentcategory': self.data['presentcategory']
                }

                model = EcBasicModel(crawl_data)
                export(model)
                data["uuid"] = model["id"]
                Scheduler.schedule(DetailCrawler.type, key=wareId, data=data)
                Scheduler.schedule(CommentCrawler.type, key=wareId, data=data)


            pages += 1


# class CommentCrawler(Crawler):
#     type = "ecommerce.jd.goodscomment"

#     def get_url(self,fid,pages):
#         one_urls = "http://gw.m.360buy.com/client.action?functionId=comment&body="
#         comment_urls = {
#             'score':'0',
#             'pagesize':'10',
#             'version':'new',
#             'wareId':str(fid),
#             'page':str(pages)

#         }
#         return one_urls + quote(str(comment_urls))

#     def crawl(self):

#         # wareId = '1229271'
#         # priorcategory = ["家居家装","清洁用品","衣物清洁"]
#         # presentcategory = ['1','2','3']
#         # ecid = '124'
#         wareId = self.key
#         ecid =  self.data['uuid']
#         category_data = extract_category(self)

#         count = 1 #页数初始值为1
#         pages = 1 #从第一页开始
#         while pages <= count:
#             number = 0 #去重
#             url = self.get_url(wareId,pages)
#             try:
#                 jsons = ProcessData.get_json_data(url)
#                 groups = jsons['commentInfoList']
#             except Exception,e:
#                 self.logger.error(e)
#                 print 'error ',url
#                 return

#             if groups == []:
#                 break
#             if pages == 1: count = math.ceil(int(groups[0]['totalCount']))
#             for i in range(len(groups)):

#                 attribute = groups[i]['attribute']
#                 for i in range(len(attribute)):
#                     if attribute[i][0]['k'] == u'心得':
#                         commentContent = attribute[0][0]['v']
#                     elif attribute[i][0]['k'] == u'购买日期':
#                         buyTime = attribute[-1][0]['v']

#                 comment_data={
#                     # 'uuid': uuid.uuid1(),         #primary key
#                     'ecid': ecid,        #commodity table foreign key
#                     'source_id': wareId,
#                     'source': self.data.get('source'),
#                     'comment_id': groups[i]['commentId'],  #review id
#                     'score': groups[i]['score'],         #commodity score
#                     'pubtime': ProcessData.str_datetime(groups[i]['creationTime']),
#                     'buytime': ProcessData.str_datetime(buyTime),
#                     'user_id': groups[i]['userId'],
#                     # 'usernickName': groups[i]['usernickName'],
#                     'useful': int(groups[i]['usefulVoteCount']),
#                     'reply': int(groups[i]['replyCount']),
#                     'content': commentContent

#                 }
#                 comment_data.update(category_data)
#                 model = EcCommentModel(comment_data)
#                 export(model)




class CommentCrawler(Crawler):
    type = "ecommerce.jd.goodscomment"
    
    def get_url(self , fid ,pages):
        url = 'http://club.jd.com/review/%s-3-%s-0.html'%(str(fid),str(pages))
        return url

    def mackining(self,name ,datas):
        data = {
            "address":"div/span/span[@class='u-address']/text()",
            "name":"div[@class='user']/div[@class='u-name']/a/text()",
            "url":"div[@class='user']/div[@class='u-name']/a/@href",
            "score":"div[@class='i-item']/div[@class='o-topic']/span/@class",
            "buytime":"div[@class='i-item']/div[@class='comment-content']/div[@class='dl-extra']/dl[last()]/dd/text()",
            "commenttime":"div[@class='i-item']/div[@class='o-topic']/span[@class='date-comment']/a/text()",
            "comment":"div[@class='i-item']/div[@class='comment-content']/dl/dd/text()",
            "title":"div[@class='i-item']/div[@class='comment-content']/dl/dd/span/span/text()",
            "commentid":"div[@class='i-item']/div[@class='o-topic']/span[@class='date-comment']/a/@href",
            "useful":"div[@class='i-item']/div[@class='btns']/div[@class='useful']/a/@title",
            "reply": "div[@class='i-item']/div[@class='btns']/a[@class='btn-reply']/@title",

        }
        xpaths = data.get(name,'')
        dom = datas[0].xpath(xpaths)
        record = ''
        for item in dom:
            if item.strip() != '':
                record += item.strip() + ' '

        return record.strip()

    def handle(self,datas):
        # print '____',datas
        data = datas.xpath("div[@class='item']")
        address = self.mackining('address',data)
        name = self.mackining('name',data)
        url = self.mackining('url',data)
        score = self.mackining('score',data)
        SCORES = re.search(u'\s*([0-5])\s*',score)
        score = int(SCORES.group(1)) if SCORES else ''
        title = self.mackining('title',data)
        comment = self.mackining('comment',data)
        commentid = self.mackining('commentid',data)
        buytime = self.mackining('buytime',data)
        useful = int(self.mackining('useful',data))
        reply = int(self.mackining('reply',data))
        buytime = ProcessData.str_datetime(buytime)
        commenttime = self.mackining('commenttime',data)
        commenttime = ProcessData.str_datetime(commenttime)

        return {
            'address': address,
            'name': name,
            'url': url,
            'score': score,
            'title': title,
            'comment': comment,
            'commentid': commentid,
            'buytime': buytime,
            'commenttime': commenttime,
            'province': address,
            'city': '',
            'useful': useful,
            'reply': reply
            # 'city': city
        }

    def crawl(self):
        # wareId = '1229271'
        # priorcategory = ["家居家装","清洁用品","衣物清洁"]
        # presentcategory = ['1','2','3']
        # ecid = '124'
        wareId = self.key
        ecid =  self.data['uuid']
        category_data = extract_category(self)
        pages = 1
        count = True
        while count: 
            number = 0    #去重
            url = self.get_url(wareId,pages)
            # print '++++++++= ',url
            html_stream = ProcessData.get_web_data(url)
            try:
                tree = etree.HTML(html_stream.text)
            except:
                print 'error: ',url
                break
            xpath = "//div[@id='comments-list']/div[@class='mc']"
            dom = tree.xpath(xpath)
            if dom == []:
                count = False
                continue
            for item in dom:
                datas = self.handle(item)
                comment_data={
                    # 'uuid': uuid.uuid1(),         #primary key
                    'ecid': ecid,        #commodity table foreign key
                    'source_id': wareId,
                    'source': self.data.get('source'),
                    'comment_id': datas['commentid'],  #review id
                    'score': datas['score'],         #commodity score
                    'pubtime': datas['commenttime'],
                    'buytime': datas['buytime'],
                    'user_id': datas['url'],
                    # 'usernickName': groups[i]['usernickName'],
                    'useful': datas['useful'],
                    'reply': datas['reply'],
                    'content': datas['comment'],
                    'province': datas['province']

                }
                comment_data.update(category_data)
                model = EcCommentModel(comment_data)
                is_saved = export(model)
                if is_saved == True:
                    pass
                else:
                    number += 1
            if number > 10:
                break
            pages += 1





class DetailCrawler(Crawler):
    type = "ecommerce.jd.goodsdetail"

    def crawl(self):
        # wareId = '1229271'
        # wareId = '1391817787'
        # priorcategory = ["家居家装","清洁用品","衣物清洁"]
        # presentcategory = ['1','2','3']
        # ids = uuid.uuid1()


        wareId = self.key
        ids =  self.data.get('uuid')
        category_data = extract_category(self)

        url = 'http://m.360buy.com/product/guige/%s.html'%(str(wareId))
        html_stream = ProcessData.get_web_data(url)
        tree = etree.HTML(html_stream.text)
        xpath = "//table[@class='Ptable']/tr/td/text()"
        dom = tree.xpath(xpath)
        specifications = {}
        temporary = ''
        i = 0
        for item in dom:
            item = item.strip()
            if item == '':
                continue
            if i%2 ==0:
                specifications[item] = ''
                temporary = extract_title(item)
            else:
                specifications[temporary] = extract_text(item)

            i += 1

        data = {
            'ecnorms':specifications
        }
        # specifications = json.dumps(specifications, ensure_ascii=False)
        introduce = IntroduceCrawler.crawl(wareId,ids)
        ecbrands = introduce[u'品牌'] if introduce.get(u'品牌') else ''
   #     ecnames = introduce[u'商品名称'].replace('\'',' ') if introduce.get(u'商品名称') else ''
        ecnames = introduce[u'商品名称'] if introduce.get(u'商品名称') else ''
        crawl_data = {
            'id': ids,
            'source': self.data.get('source'),
            'source_id': wareId,
            'summary': specifications,
            'introduce': introduce,
            'name': ecnames,
            'brand': ecbrands
        }
        crawl_data.update(category_data)
        model = EcDetailModel(crawl_data)
        export(model)


#class IntroduceCrawler(Crawler):
#    type = "ecommerce.jd.goodsintroduce"
class IntroduceCrawler:
    @staticmethod
    def crawl(wareId,ids ):
        import sys
        reload(sys)
        sys.setdefaultencoding("utf-8")

        url = 'http://item.jd.com/%s.html'%(str(wareId))
        html_stream = ProcessData.get_web_data(url)
        if html_stream=={}:
            return {}
        html_stream.encoding = 'gb2312'
        tree = etree.HTML(html_stream.text)
        xpath = "//div[@id='product-detail-1']/ul[@class='detail-list']/li//text()"
        dom = tree.xpath(xpath)
        introduce = {}
        temporary = ''
        for item in dom:
            item = item.strip()
            if item == '':
                continue
            elif item.find('：') >0:
                item = item.split('：',1)
                if item[1] == '':
                    temporary = extract_title(item[0])
                else:
                    introduce[extract_title(item[0])] = extract_text(item[1])
            else:
                if temporary != '':
                    introduce[temporary] = extract_text(item)
                    temporary = ''
                else:
                    continue

        if introduce != '':
            return introduce
        else:
            return ''


class UserCrawler(Crawler):
    type = "ecommerce.jd.userinfo"

    def cralw(self):
        pass


if __name__ == "__main__":
    # f = DetailCrawler()
    # f.crawl()
    # t = uuid.uuid1()
    # data = {
    #     'source': 'jd',
    #     'priorcategory' :["家居家装","清洁用品","衣物清洁"],
    #     'presentcategory':["家居家装","清洁用品","衣物清洁"]
    #     }
    # ListCrawler(key='11052',data=data).crawl()


    t = uuid.uuid1()
    data = {
        'source': 'jd',
        'priorcategory' :["家居家装","清洁用品","衣物清洁"],
        'presentcategory':["家居家装","清洁用品","衣物清洁"],
        'uuid': t
        }
    CommentCrawler(key='1229271',data=data).crawl()