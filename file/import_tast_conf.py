#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
SRC_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(SRC_PATH)

from pymongo import MongoClient
from datetime import datetime
from settings import MONGO_CONN_STR,CASSA_CONN_STR

def read_task():
    bk = xlrd.open_workbook('weixin.xls')
    sh = bk.sheet_by_name('Sheet1')

    return sh
    # nrows = sh.nrows
    # ncols = sh.ncols
    # for i in xrange(1,nrows):
    #     pass

class MongoDB():
    _conn = MongoClient(MONGO_CONN_STR)
    _db = _conn["crawler"]

MGdb = MongoDB()._db

class Task(dict):

    staticmethod
    def get_conf(self, data):
        crawler_conf = {
            "type" : data.get('type',''),
            "status" : data.get('status', 1),
            "priority" : data.get('priority',3),
            "interval" : data.get('interval', 7200),
            "updated" : datetime.utcnow()
        }
        return crawler_conf

    def conf(self, types):
        assert isinstance(types, list)
        for item in types:
            self.task_conf(item)

    def task_conf(self, type):
        data = {}
        data = {
            'type': type,
            }
        if not MGdb.crawler_conf.find_one({'type': data.get('type')}):
            MGdb.crawler_conf.insert(self.get_conf(data))
            print 'success'
        # else:
        #     print 'exist'

class SearchTask(Task):

    def insert_conf(self):
        # type1 = "search_hot.baidu.newstitle"
        # type2 = "search.baidu.newscontent"
        types = [
            "zjld.baidu.newstitle",
            "zjld.baidu.newscontent"
        ]
        self.conf(types)

class WeiboTask(Task):

    def insert_conf(self):
        types = [
            "zjld.weibo.firstlvl",
            "zjld.weibo.newscontent",
            "weibo_hot.weibo.hot",
            "zjld.weibo.newsarticle",
            "zjld.weibo.newstitle",
        ]
        self.conf(types)

class WeixinTask(Task):

    def insert_conf(self):
        types = [
            "zjld.sogou.keywords",
            "zjld.sogou.firstlvl",
            "zjld.sogou.keywords",
            "zjld.sogou.newscontent",
           
        ]
        self.conf(types)

class ArticleTask(Task):

    def insert_conf(self):

        conf = {
            'cqn': u'中国质量新闻网',
            'fjqi': u'福建质监局',
            'hzqts': u'浙江杭州质监局',
            'jxzj': u'江西质监局',
            'sdqts': u'山东质监局',
            'zjbts': u'浙江质监局',
            'gdqts': u'广东质监局',
            'aqsiq': u'国家质量监督检验检疫总局',
            'hbzljd': u'湖北质监局',
            'bjtsb': u'北京质监局',
            'gzq': u'广东广州质监局',
            'fsjsjd': u'广东佛山质监局',
            'zhqc': u'广东珠海质监局',

            'yuqing': u'以前的爬虫',
        }
        types = []
        for item in conf.keys():
            type1 = 'zjld.' + item + '.firstlvl'
            type2 = 'zjld.' + item + '.newscontent'
            types.append(type1)
            types.append(type2)
        self.conf(types)
            

if __name__ == "__main__":
    # print CASSA_CONN_STR
    SearchTask().insert_conf()
    print '--'
    WeiboTask().insert_conf()
    print '----'
    WeixinTask().insert_conf()
    print '--'
    ArticleTask().insert_conf()