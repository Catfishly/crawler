#!/usr/bin/python
# encoding=utf-8

import sys  
reload(sys)  
sys.setdefaultencoding("utf8")
from urllib import quote, unquote
import urllib
import requests
from lxml import etree
from datetime import datetime
import time


import multiprocessing
import time

 
import subprocess
p = subprocess.Popen('ls',stdout=subprocess.PIPE)
print p.stdout.readlines()


''''' 
子进程结束会向父进程发送SIGCHLD信号 
'''  
"""
import os  
import signal  
from time import sleep  
   
def onsigchld(a,b):  
    print '收到子进程结束信号'  ,a,b
signal.signal(signal.SIGCHLD,onsigchld)  
   
pid = os.fork()  
if pid == 0:  
   print '我是子进程,pid是',os.getpid() 
   sleep(2)  
else:  
    print '我是父进程,pid是',os.getpid()  ,pid
    os.wait()  #等待子进程结束  





def func(msg):
    for i in xrange(3):
        print msg
        time.sleep(1)
 
# if __name__ == "__main__":
#     p = multiprocessing.Process(target=func, args=("hello", ))
#     p.start()
#     # p.join()
#     print "Sub-process done."

class ModelMeta(type):
    def __init__(self, name, bases, dct):
        #pass
        FIELDS = {'dd':'d'}
        fields = dct.get('FIELDS', {})
       # print '====',fields
        base = bases[0]
        # print 'base.__base__1',base.__dict__.get('FIELDS', {})
        # print 'base.__base__2',base
        # print "base.__dict__.get('FIELDS', {})",base.__dict__.get('FIELDS', {})
        while base != object:
            for k, v in base.__dict__.get('FIELDS', {}).iteritems():
                fields[k] = v
                print k,v
            base = base.__base__
          #  print '+++++base ',base
        dct['FIELDS'] = fields

        indexes = dct.get('INDEXES', [])
        base = bases[0]
        while base != object:
            indexes.extend(base.__dict__.get('INDEXES', []))
            base = base.__base__
        dct['INDEXES'] = indexes

        type.__init__(self, name, bases, dct)


class b(dict):
    type ='b'
    __metaclass__ = ModelMeta
    FIELDS = {
    'b' : 'b',
    'c' : 'c',
    'a' : 'dd'
    }
    INDEXES = ['1','2']
    def __init__(self, dct={}):
        print 'b = ',self.FIELDS

    def __setitem__(self, key, value):
        return self.set_field(key, value)
class a(b):
    type = 'a'
    FIELDS = {
    'a' : 'aa',
    'x' : 'x'
    }
    xx = 0
    # def __del__(self, dct={}):
    #     print 'xx del=1 ',a.xx
    #     a.xx -= 1
    #     print 'xx del=2 ',a.xx
    def __init__(self, dct={}):
        super(a, self).__init__(dct)
        a.xx += 5
        print 'xx init= ',a.FIELDS
    # def aa(self):
    #     print '-----',a.xx
    # def __del__(self, dct={}):
    #     a.xx -= 1
    #     print 'xx del= ',a.xx

aa = {'xx':'xx'}
x = a(aa)
# x.aa()










#url ='http://mp.weixin.qq.com/s?__biz=MjM5ODExMjg0MQ==&mid=203299354&idx=3&sn=9e5306ac080e55dbc8095237f61cb524&3rd=MzA3MDU4NTYzMw==&scene=6#rd'
url = 'http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid=oIWsFt2sFmMXiDf2BGLZYZ0LDcJ4'

cookies2 = dict(SUID ='6A7A6077260C930A0000000054F1AEA1',
    SNUID='CEDEC4D3A3A6B3807E1F8F9FA413F110',
    IPLOC='CN4201',
    ABTEST='1|1425125024|v1',
    SUIR='1425125025',
    SUV='1425125409602000633')
cookies1 = dict(SUID ='6A7A6077260C930A0000000054F1B1C9',
    SNUID='26312C3C4C495B6FBC4638AD4C4EAC78',
    IPLOC='CN4201',
    ABTEST='1|1425125833|v1',
    SUIR='1425125833',
    SUV='142512583308500066')

class prodata():
    def get_web_data(self, url):
        listips = {
        'http://183.207.224.42:80': 'http', 
        'http://180.153.100.242:80': 'http',
         'http://122.72.124.42:80': 'http', 
         'http://122.72.12.178:80': 'http', 
         'http://182.254.138.114:80': 'http', 
         'http://183.207.228.7:80': 'http',
            'http://120.24.59.17:80': 'http'}
#786ADB052125306AC718356B218138FA
        i_headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5",
                     "Referer": 'http://weixin.sogou.com'}
        s = requests.Session()
        s.proxies = {
            'http': listips.keys()[4]
        }
        html_stream = s.get(url, timeout=5)
        print url
        return html_stream


    def getIP(self, size):
        # ip列表
        ips = {}

        # 爬取的网站
        url = "http://www.kjson.com/proxy/search/1/?sort=down&by=asc&t=highavailable"
        # 获取流
        html_stream = requests.get(url, timeout=5)
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
                    ip = ipitem.xpath("td[1]/text()")
                    tmplist = {"http://" + ip[0] + ":" + prot: "http"}
                    ips.update(tmplist)

        return ips
#print prodata().getIP(1)

# while 1:
#     html_stream = requests.get(url,cookies=cookies2)
#     html_stream.encoding = 'GBK'
#     print 'len = ',len(html_stream.text)#len =  789
#     print '===',html_stream.text[1000:1300]
#     break
#print prodata().get_web_data(url).text
# date = new Date();
# SUV = date.getTime())*1000+Math.round(Math.random()*1000)


import time
#from datetime import *
#1425125833
#1425363799
# a = time.localtime(time.time())
# print time.strftime('%H',time.localtime(time.time()))

# if int(time.strftime('%H',time.localtime(time.time())))%4 == 0:
#     print '==='


"""
