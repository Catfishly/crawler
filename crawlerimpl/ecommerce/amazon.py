# coding: UTF-8
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    author:bing gong
    time: 2014-11-28
    vision:v.1.0
    rebark: amzazon   爬虫代码编写
    
'''
import sys
import requests
import uuid


root_mod = '/bgong/workspace/dianshangCrawlerWorkspace/crawler'
sys.path.append(root_mod)
# xml解析问题


from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce.model import EcBasicModel, EcDetailModel, EcCommentModel
from processdata import extract_title, extract_category, extract_text
# python操作mongodb
import pymongo
from datetime import datetime, timedelta
import time
import json

from settings import MONGO_CONN_STR

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

'''
    说明:获取亚马逊一级分类
'''
reload(sys)
# 解决utf-8乱码问题
sys.setdefaultencoding("utf-8")  # @UndefinedVariable

''' 
    系统初始化，获取10个动态代理ip
'''
listips = {}
ipindex = 0
'''
    获取网页的流数据，如果出现异常，可以在爬取一次
'''


class ProcessData():

    @staticmethod
    def str_datetime(str_time):
        str_time = str_time.strip()
        time_format = '%Y-%m-%d %H:%M:%S'
        times = datetime.strptime(str_time, time_format) - timedelta(hours=8)
        return times

    @staticmethod
    def get_web_data(url):

        # 设置浏览器访问
        i_headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5",
                     "Referer": 'http://www.amazon.cn'}
        count = 0

        # 设置ip代理
        s = requests.Session()

        global ipindex
        global listips

        # ip代理列表

        if len(listips) == ipindex:
            ipindex = 0

        s.proxies = {
            'http': listips.keys()[ipindex]
        }

        ipindex += 1
        # print s.proxies

        while count < 2:
            try:
                html_stream = s.get(url, timeout=5, headers=i_headers)

            except requests.exceptions.Timeout:
                count += 1

                if count == 2:
                    l = ProcessData().getIP(1)
                    listips.pop(listips.keys()[ipindex])  # 移除该方法
                    listips.update(l)

            except:
                return {}
            else:
                break
        return html_stream

    '''
    动态获取代理ip 
    '''

    def getIP(self, size):
        # ip列表
        ips = {}

        # 爬取的网站
        url = "http://www.kjson.com/proxy/search/1/?sort=down&by=asc&t=highavailable"
        # 获取流
        html_stream = requests.get(url, timeout=5)

#
# 获取html
        html = etree.HTML(html_stream.text)

        content = "//table[@id='proxy_table']/tr"

        iplist = html.xpath(content)

        for ipitem in iplist:

            # 获取端口
            status = ipitem.xpath("td[@class='enport']/text()")

            prot = "0"

            if status != None and status != [] and status[0] == "DCA":
                prot = "80"

                # 值获取http类型
                type = ipitem.xpath("td[3]/text()")
                if type[0] == "HTTP":

                    # if len(ips) < size :

                    # 获取ip
                    ip = ipitem.xpath("td[1]/text()")
                    # print ip[0]+"   "+prot
                    # tmplist={"http":"http://"+ip[0]+":"+prot}
                    tmplist = {"http://" + ip[0] + ":" + prot: "http"}
                    ips.update(tmplist)

        return ips

'''
    获取一级二级三级分类信息,把分类信息存储到mongodb中
'''


class FirstCrawler(Crawler):

    type = "ecommerce.amazon.firstlvl"

    @staticmethod
    def init(conf=None):
        pass
    #    Scheduler.schedule(FirstCrawler.type, interval=86400)
        # 获取10个动态ip
        global listips
        listips = ProcessData().getIP(10)

    def crawl(self):

        url = "http://www.amazon.cn/gp/site-directory"
        # 获取该url的流信息
        html_stream = ProcessData.get_web_data(url)
        # 获取html 信息
        html = etree.HTML(html_stream.text)

        # 整个一级二级三级分类的xpath
        xpath = "//div[@id='siteDirectory']/div[@class='a-row']/div[@class='a-row a-spacing-small a-spacing-top-medium']"

        dom = html.xpath(xpath)

        # 获取一级分类
        onexpath = "div[@class='a-row a-spacing-extra-large a-spacing-top-small']/span/a"

        # binali
        tmp = "div[@class='a-row a-spacing-none a-spacing-top-mini sd-addPadding']/div[@class='a-column a-span3 sd-colMarginRight']"

        # 获取二级分类
        twoxpath = "div[@class='a-column a-span12 sd-columnSize']/div[@class='a-row a-spacing-small']/span[@class='sd-fontSizeL2 a-text-bold']/a"

        threexpath = "div[@class='a-column a-span12 sd-columnSize']/div[@class='a-row a-spacing-small']/div[@class='a-row']/ul/li/span/span/a"

        # 连接mongodb
        conmn = pymongo.Connection(MONGO_CONN_STR)

        for item in dom:
            # 获取一级分类  a-row a-spacing-extra-large a-spacing-top-small
            oneitem = item.xpath(onexpath)
            oneinfo = ""

            # print oneitem

            for one in oneitem:
                oneinfo += one.text + ";"

            # 获取一级分类
            oneinfo = oneinfo[:-1]
            # 把一级分类存储到mongodb中
            conmn.crawler.ecommerce.save({'priority': 1, 'status': 1, 'timeout': 3600, 'key': '', 'data':
                                          {
                                              'priorcategory': [oneinfo],
                                              'presentcategory': {"1": ''}
                                          },
                                          "interval": 0,
                                          "type": "ecommerce.amazon.firstlvl"})

            tmpxpath = item.xpath(tmp)

            for itemtmp in tmpxpath:
                twoitem = itemtmp.xpath(twoxpath)
                i = 0
                for two in twoitem:

                    conmn.crawler.ecommerce.save({'priority': 1, 'status': 1, 'timeout': 3600, 'key': two.get("href"), 'data':
                                                  {
                        'priorcategory': [oneinfo, two.text],
                        'presentcategory': {"1": '', "2": ''}
                    },
                        "interval": 0,
                        "type": "ecommerce.amazon.goodsdetail"})

                    threeitem = itemtmp.xpath(
                        "div[@class='a-column a-span12 sd-columnSize']/div[@class='a-row a-spacing-small']/div[@class='a-row']")

                    tmpc = threeitem[i].xpath("ul/li/span/span/a")
                    for t in tmpc:
                        conmn.crawler.ecommerce.save({'priority': 1, 'status': 1, 'timeout': 3600, 'key': t.get("href"), 'data':
                                                      {
                            'priorcategory': [oneinfo, two.text, t.text],
                            'presentcategory': {"1": '', "2": '', "3": ''}
                        },
                            "interval": 0,
                            "type": "ecommerce.amazon.firstlvl"})

                        # 执行列表
                        Scheduler.schedule(ListCrawler.type, key=t.get("href"), data={
                            'priorcategory': [oneinfo, two.text, t.text],
                            'presentcategory': {"1": '', "2": '', "3": ''}
                        })

                    i = i + 1


'''
    获取商品列表
'''


class ListCrawler(Crawler):

    type = "ecommerce.amazon.goodslist"

    def get_url(self, keyid, page):
        start_url = "http://www.amazon.cn" + keyid + "&page=" + str(page)

        return start_url

    def crawl(self):
        # 获取key 信息
        # keyid="/%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/b?ie=UTF8&node=106200071"
        keyid = self.key
        source = "amazon"
        score = 0  # 评分
        # 获取原始分类
        category_data = extract_category(self)
        # priorcategory
        priorcategory = self.data["priorcategory"]
        presentcategory = self.data["presentcategory"]

        count = getPageSize(self.get_url(keyid, 1))  # 页数初始值为3
        page = 1  # 从第一页开始

        content = "//div[@id='mainResults']/div"

        while page <= count:
            # 获取url信息
            url = self.get_url(keyid, page)

            # print url
            # 获取该url的流信息
            html_stream = ProcessData.get_web_data(url)

            # self.logger.info("执行页面:"+url)
            # 获取商品列表的html 信息
            html = etree.HTML(html_stream.text)

            # 获取整个商品的某一个商品的选项,返回的是一个列表
            itempath = html.xpath(content)

            if itempath != None and itempath != []:
                # print itempath
                for item in itempath:
                    title = item.xpath("h3[@class='newaps']/a")
                # crawl_data=[]  #存储数据
                # jg=item.xpath("")
                    # 价格
                    pric = item.xpath(
                        "ul[@class='rsltGridList grey']/li[@class='newp']/div")

                    if pric == None:

                        pric = item.xpath("ul/li[@class='newp']/div")

                    # 商品评分
                    socreitmem = item.xpath(
                        "ul[@class='rsltGridList grey']/li[@class='rvw']/span/span/a")

                    if socreitmem != []:
                        scoreinfo = socreitmem[0].get('alt')
                        if scoreinfo != None:
                            score = float(scoreinfo[2:-1])

                    for t in title:
                        # 获取商品的标题和url
                        original_price = u"￥0.00"

                        if pric == None or pric == []:
                            price = u"￥0.00"
                        else:
                            try:
                                price = pric[0].xpath("a/span")[0].text
                            except:
                                print url
                                print "出错价格" + pric

                        if pric != None and pric != [] and pric[0].xpath("a/del") != []:
                            # 有原价
                            original_price = pric[0].xpath("a/del")[0].text
                        else:
                            # 如果没有原价，那就可以现价一样
                            original_price = price

                # i+=1
                    # 把信息存储到mongodb中
                        data = {
                            'priorcategory': priorcategory,
                            'presentcategory': presentcategory
                        }

                        if price != None and price.strip() != '' and pric != [] and pric[0] != '':

                            # self.logger.info("价格:"+price)
                            # 把信息存储到cassandra中
                            try:
                                float(price.strip()[1:].replace(",", ""))
                                # float(original_price.strip()[1:].replace(",","")
                            except:
                                self.logger.error("错误price:" + price)
                                self.logger.error("错误price:" + original_price)

                            crawl_data = {
                                # 'id': uuid.uuid1(),
                                'source_id': t.get("href"),
                                'source': source,
                                'summary': {},
                                'title': t.xpath("span")[0].text,
                                'adword': '',
                                'price': float(price.strip()[1:].replace(",", "")),
                                'original_price': float(original_price.strip()[1:].replace(",", "")),
                                'score': 0
                            }

                            crawl_data.update(category_data)
                # 保存到cassandra数据库中category_data
                            model = EcBasicModel(crawl_data)
                            export(model)
                            data["uuid"] = model["id"]

                            # print "执行存储cassandra...."
                            Scheduler.schedule(
                                DetailCrawler.type, key=t.get("href"), data=data)
                            Scheduler.schedule(
                                CommentCrawler.type, key=t.get("href"), data=data)
                    # print repr(json.dumps(crawl_data))
            page += 1


''''
    列表的内容id号为 atfResults  的分类
'''
# class ListCrawlerByatfResults(Crawler):
#
#     type = "ecommerce.amazon.goodslist"
#
#     def get_url(self,keyid,page):
#         start_url="http://www.amazon.cn"+keyid+"&page="+str(page)
#
#         return start_url
#
#     def crawl(self):
# 获取key 信息
# keyid="/%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/b?ie=UTF8&node=106200071"
#         keyid=self.key
#         source = "amazon"
# 获取原始分类
#         category_data = extract_category(self)
# priorcategory
#         priorcategory=self.data["priorcategory"]
#         presentcategory=self.data["presentcategory"]
#
#
# count = 3# 页数初始值为3
# page = 1 # 从第一页开始
#
#         while page<=count:
# 获取url信息
#              url = self.get_url(keyid, page)
#
#              print url
# 获取该url的流信息
#
#              html_stream = ProcessData.get_web_data(url)
# 获取商品列表的html 信息
#              html = etree.HTML(html_stream.text)
#
#              print html.text
#
# self.crawlHtml(html)
#
#              page+=1
#
#
#
#
#     def crawlHtml(self,html):
#         keyid=self.key
#         source = "amazon"
# 获取原始分类
#         category_data = extract_category(self)
# priorcategory
#         priorcategory=self.data["priorcategory"]
#         presentcategory=self.data["presentcategory"]
#
#
#
#         content="//div"
#
# 获取整个商品的某一个商品的选项,返回的是一个列表
#         itempath=html.xpath(content)
#
#
#         for item in itempath:
#             print item
# 商品列表 内容
# divitem=item.XPATH("div[@class='a-row a-spacing-mini']")
# #
# title=divitem[0].XPATH("div/a/text()")[0]
# print title
#
#
# class ListCrawler2(Crawler):
#
#     type = "ecommerce.amazon.goodslist"
#
#     def get_url(self,keyid,page):
#         start_url="http://www.amazon.cn"+keyid+"&page="+str(page)
#
#         return start_url
#
#
#     def crawl(self):
# 获取key 信息
# keyid="/%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/b?ie=UTF8&node=106200071"
#         keyid=self.key
#         source = "amazon"
# 获取原始分类
#         category_data = extract_category(self)
# priorcategory
#         priorcategory=self.data["priorcategory"]
#         presentcategory=self.data["presentcategory"]
#
#
# count = 3 # 页数初始值为3
# page = 1 # 从第一页开始
#
#         content="//div[@id='a-page']"
#
#
#         while page<=count:
# 获取url信息
#              url = self.get_url(keyid, page)
#
#              print url
# 获取该url的流信息
#              html_stream = ProcessData.get_web_data(url)
# 获取商品列表的html 信息
#              html = etree.HTML(html_stream.text)
# content="//div[@id='atfResults']/ul/li"
# #
# 获取整个商品的某一个商品的选项,返回的是一个列表
#              itempath=html.xpath(content)
#
#              print itempath
#              page+=1


'''
    获取具体的商品信息,把信息存储到cassandra中--电脑方面信息,具备产品参数和技术参数
'''


class DetailCrawler(Crawler):
    type = "ecommerce.amazon.goodsdetail"

    def crawl(self):

        # id号
        ids = self.data['uuid']
        # ids="1dcfa11e-7acf-11e4-b0cc-00e06668ddd1"
        # source_id=""
        # 商品url信息
        url = self.key

        print "url:" + url

        source = "amazon"

        category_data = extract_category(self)

        # 获取该url的流信息
        html_stream = ProcessData.get_web_data(url)

        # 获取商品列表的html 信息
        html = etree.HTML(html_stream.text)

        # 获取商品的详细信息
        prodDetails = html.xpath("//div[@id='prodDetails']")

        if len(prodDetails) == 0:
            # 获取模版也具有基本信息的数据
            detailed = getDetailedGoods(
                type=self.type,
                key=self.key,
                data=self.data
            ).crawlHtml(html)
        else:
            # 打印商品样式
            style = prodDetails[0].xpath("div[@class='disclaim']/strong")
           # print style[0].text

        # 获取具体商品信息
            goodinfo = prodDetails[0].xpath(
                "div[@class='wrapper CNlocale']//table/tbody/tr")

        # 商品
            summary = {}
            ecbrands = ""
            ecnames = ""
            introduce = {}

            for info in goodinfo:
                # print
                # info.xpath("td[@class='label']")[0].text,info.xpath("td[@class='value']")[0].text
                if info.xpath("td[@class='label']") != []:
                    if info.xpath("td[@class='label']")[0].text == "用户评分":
                        summary[info.xpath("td[@class='label']")[0].text] = info.xpath("td[@class='value']")[
                            0].xpath("//div[@id='averageCustomerReviewRating']")[0].text.strip()[2:-1]
                    # print
                    # info.xpath("td[@class='label']")[0].text,info.xpath("td[@class='value']")[0].xpath("//div[@id='averageCustomerReviewRating']")[0].text.strip()[2:-1]
                    elif info.xpath("td[@class='label']")[0].text.strip() == "品牌":
                        ecbrands = info.xpath(
                            "td[@class='value']")[0].text.strip()
                    else:
                        summary[info.xpath("td[@class='label']")[0].text] = info.xpath(
                            "td[@class='value']")[0].text.strip()
                    # print
                    # info.xpath("td[@class='label']")[0].text,info.xpath("td[@class='value']")[0].text.strip()

                    # 存入cassandra中
            crawl_data = {
                'id': ids,
                'source': source,
                'source_id': url,
                'summary': summary,
                'introduce': introduce,
                'name': ecnames,
                'brand': ecbrands
            }

            crawl_data.update(category_data)
            # print crawl_data
            model = EcDetailModel(crawl_data)
            export(model)


'''
    获取具备基本信息的数据
'''


class getDetailedGoods(Crawler):

    # 执行爬虫数据
    def crawl(self):
        # 获取url信息
        url = self.key
        # 获取该url的流信息
        html_stream = ProcessData.get_web_data(url)

        # 获取商品列表的html 信息
        html = etree.HTML(html_stream.text)
        self.crawlHtml(html)

    def crawlHtml(self, html):

        ids = self.data['uuid']
        source = "amazon"
        source_id = self.key
        category_data = extract_category(self)
        summary = {}
        ecbrands = ""
        ecnames = ""
        introduce = {}
        # 获取  productDetailsTable
        prodDetails = html.xpath(
            "//table[@id='productDetailsTable']//tr/td[@class='bucket']/div[@class='content']/ul/li")

        for proditem in prodDetails:

            k = proditem.xpath("b/text()")[0].strip()[:-1]

            if k == "用户评分":
                summary[k] = proditem.xpath(
                    "span[@class='crAvgStars']/span/a/span/span/text()")[0].strip()[2:-1]
                # print
            elif k == "亚马逊热销商品排名":
                print "a"
            else:
                summary[k] = proditem.xpath("text()")[0].strip()

        crawl_data = {
            'id': ids,
            'source': source,
            'source_id': source_id,
            'summary': summary,
            'introduce': introduce,
            'name': ecnames,
            'brand': ecbrands
        }
        crawl_data.update(category_data)
        # print crawl_data
        model = EcDetailModel(crawl_data)
        export(model)

        # 商品的详细参数
        # inro=html.xpath("//div[@id='iframe-wrapper']//h2")
        # print inro
        # if len(inro) > 0 :
        #     listinro=inro[0].xpath("//div[@class='productDescriptionWrapper']/br/text()")
        #     for inroitem in listinro:
        #         print inroitem

'''
    评论信息存储
'''


class CommentCrawler(Crawler):

    type = "ecommerce.amazon.goodscomment"

    # 获取评论url信息
    def get_url(self, url, page):
        tmpu = url[url.index("/dp/") + 4:]
        # print tmpu[0:tmpu.index("/")]
        return "http://www.amazon.cn/product-reviews/" + tmpu[0:tmpu.index("/")] + "/ref=cm_cr_dp_see_all_summary?ie=UTF8&showViewpoints=1&sortBy=byRankDescending&pageNumber=" + str(page)

    def crawl(self):

        #商品id, 需要获取
        goodid = self.data['uuid']
       # goodid="7ebd0a6a-7b5c-11e4-85d7-00e06668ddd1"
        source = "amazon"

        url = self.key
        source_id = url
        category_data = extract_category(self)

        count = getCommSize(self.get_url(url, 1))  # 页数初始值为3
        page = 1  # 从第一页开始

        while page <= count:
            newurl = self.get_url(url, page)
            print newurl
        # productReviews

         # 获取该url的流信息
            html_stream = ProcessData.get_web_data(newurl)

        # 获取商品列表的html 信息
            html = etree.HTML(html_stream.text)
            # 获取评论区
            comment = html.xpath("//table[@id='productReviews']//tr/td/div")

            for comitem in comment:
                # None

                 # 评论内容
                item = comitem.xpath("div[@class='reviewText']//text()")

                # 评分
                scoreitem = comitem.xpath(
                    "div[@style='margin-bottom:0.5em;']/span/span/span")
                # 发布时间
                pubtimeitem = comitem.xpath(
                    "div[@style='margin-bottom:0.5em;']/span[@style='vertical-align:middle;']/nobr")

                # 用户的链接地址
                user_iditem = comitem.xpath(
                    "div[@style='margin-bottom:0.5em;']/div/div[@style='float:left;']/a")

                # 有用信息
                usefulitem = comitem.xpath(
                    "div[@style='margin-bottom:0.5em;']")

                oninfo = ""
                for i in item:
                    oninfo += i

                # 有用和无用信息
                if usefulitem != None and usefulitem != []:
                    tmpuseful = usefulitem[0].text.strip()
                else:
                    tmpuseful = "0"

                if tmpuseful == "":
                    tmpuseful = "0"
                elif tmpuseful != "0":
                    tmpuseful = tmpuseful[0:tmpuseful.index("/")]

                # 日期
                pubtim = datetime.strptime("1971-01-1", '%Y-%m-%d')
                if pubtimeitem != None and pubtimeitem != []:
                    pubtim = datetime.strptime(pubtimeitem[0].text.replace(
                        "年", "-").replace("月", "-").replace("日", ""), '%Y-%m-%d')

                # 把日期的字符串类型，转换成日期类型

                sorce = "0.0"

                if scoreitem != None and scoreitem != []:
                    sorce = scoreitem[0].text[2:-1].strip()
                    # print "评分:"+sorce

              #  print user_iditem
                userid = ''
                if user_iditem != None and user_iditem != []:
                    userid = str(user_iditem[0].get("href"))

                comment_data = {
                    "ecid": goodid,
                    "source_id": source_id,
                    "source": source,
                    "comment_id": "",
                    "pubtime": pubtim,
                    "buytime": pubtim,
                    "score": float(sorce),
                    "user_id": userid,
                    "useful": int(tmpuseful),
                    'reply': 0,
                    "content": oninfo.strip()
                }
#                print comment_data
            # 把原始和现有分类存储到数据库中
                comment_data.update(category_data)

                model = EcCommentModel(comment_data)
                export(model)
            page += 1


''' 
 获取商品url列表的页数
'''


def getPageSize(url):
    size = 1

    html_stream = ProcessData.get_web_data(url)

    # 获取商品列表的html 信息
    html = etree.HTML(html_stream.text)

    cont = "//div[@id='pagn']/span[@class='pagnDisabled']/text()"

    sizestr = html.xpath(cont)
    if sizestr != None and sizestr != []:
        size = int(sizestr[0])
    return size

'''
    获取商品评论的评论页数
'''


def getCommSize(url):

    size = 1
    html_stream = ProcessData.get_web_data(url)

    print html_stream
    # 获取商品列表的html 信息
    print url
    html = etree.HTML(html_stream.text)

    cont = "//span[@class='paging']/a/text()"

    cont1 = "//div[@class='cdPageSelectorPagination']/a/text()"
    page = html.xpath(cont)

    if page == []:
        page = html.xpath(cont1)

    if page != None and page != []:
        size = page[len(page) - 2]

    if size > 500:
        size = 500

    return size


if __name__ == "__main__":
    # http://www.amazon.cn/gp/forum/cd/discussion.html/ref=cm_cd_dp_aar_al_a?ie=UTF8&asin=B00OB5T6N2&cdForum=Fx3PMCD87L9N4NG&cdThread=TxY709BKFOJW8D
        # print
        # getCommSize("http://www.amazon.cn/product-reviews/B00IDZKB9O/ref=cm_cr_dp_see_all_summary?ie=UTF8&showViewpoints=1&sortBy=byRankDescending")

        # classify=GetClassify()
        # classify.crawl("http://www.amazon.cn/gp/site-directory")

        # 商品列表
    #       urllist=ListCrawler(
    #       type='ecommerce.jd.goodsdetail',
    #       key='/%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/b?ie=UTF8&node=106200071',
    #      data={
    #      "priorcategory" : [ "电脑;办公" , "电脑整机" , "笔记本"] ,
    #      "presentcategory" : ["电脑;办公" , "电脑整机" , "笔记本" ]
    #      }
    #       )
    #       urllist.crawl()

    #
    #     urllist=ListCrawlerByatfResults(
    #       type='ecommerce.jd.goodsdetail',
    #     key='/%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/b?ie=UTF8&node=106200071',
    #
    # key='/b/ref=sd_allcat_applia_l3_b2132893051?ie=UTF8&node=2132893051',
    #      data={
    #      "priorcategory" : [ "电脑;办公" , "电脑整机" , "笔记本"] ,
    #      "presentcategory" : ["电脑;办公" , "电脑整机" , "笔记本" ]
    #      }
    #       )
    #     urllist.crawl()

    #     urllist=ListCrawler2(
    #       type='ecommerce.jd.goodsdetail',
    #       key='/b/ref=sd_allcat_applia_l3_b2132893051?ie=UTF8&node=2132893051',
    # key='/%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/b?ie=UTF8&node=106200071',
    #      data={
    #      "priorcategory" : [ "电脑;办公" , "电脑整机" , "笔记本"] ,
    #      "presentcategory" : ["电脑;办公" , "电脑整机" , "笔记本" ]
    #      }
    #       )
    #     urllist.crawl()

      # 商品的详细信息
      # good=getGoods(
      #   type='ecommerce.jd.goodsdetail',
      #   key='http://www.amazon.cn/Apple-MacBook-Pro-MD101CH-A-13-3%E8%8B%B1%E5%AF%B8%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/dp/B008FWHFLW/ref=lp_106200071_1_34?s=pc&ie=UTF8&qid=1417575028&sr=1-34',
      #  data={
      #  "priorcategory" : [ "电脑;办公" , "电脑整机" , "笔记本"] ,
      #  "presentcategory" : ["电脑;办公" , "电脑整机" , "笔记本" ]
      #  },
      #  'uuid':uuid.uuid1()
      #   )
      # good.crawl()

     # 商品评论
     # 商品评论到cassandra
    comment = CommentCrawler(type='ecommerce.jd.goodsdetail',
                             key='http://www.amazon.cn/Apple-MacBook-Pro-MD101CH-A-13-3%E8%8B%B1%E5%AF%B8%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/dp/B008FWHFLW/ref=lp_106200071_1_34?s=pc&ie=UTF8&qid=1417575028&sr=1-34',
                             data={
                                 "priorcategory": ["电脑;办公", "电脑整机", "笔记本"],
                                 "presentcategory": ["1", "3", "2"], 'uuid': uuid.uuid1()
                             })
    comment.crawl()

    # detailed=getGoods(
    #     type='ecommerce.jd.goodsdetail',
    #     key='http://www.amazon.cn/%E7%BA%A2%E7%B1%B3-note-%E7%A7%BB%E5%8A%A84G%E5%A2%9E%E5%BC%BA%E7%89%88-TDD-LTE-TD-SCDMA-GSM-%E7%A7%BB%E5%8A%A84G-%E6%89%8B%E6%9C%BA-2G-RAM-%E9%AB%98%E9%80%9A%E9%AA%81%E9%BE%99400%E5%9B%9B%E6%A0%B8%E5%A4%84%E7%90%86%E5%99%A8-5-5%E8%8B%B1%E5%AF%B8%E9%AB%98%E6%B8%85IPS%E5%B1%8F%E5%B9%95-1300%E4%B8%87-500%E4%B8%87%E5%83%8F%E7%B4%A0%E7%9B%B8%E6%9C%BA/dp/B00MO66F7A/ref=sr_1_1?s=wireless&ie=UTF8&qid=1418011384&sr=1-1',
    #    data={
    #    "priorcategory" : [ "电脑;办公" , "电脑整机" , "笔记本"] ,
    #    "presentcategory" : ["1"  , "3" , "2" ],
    #    "uuid":uuid.uuid1()
    #    }
    #     )
    # detailed.crawl()

#     pro=ProcessData()
#
#     iplist=pro.getIP(10)
#     print iplist
