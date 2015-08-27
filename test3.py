#!/usr/bin/python
# Filename: objvar.py
from urllib import quote ,unquote
import requests
import re
import time,random
def get_cookies():
    cookies = []
    print 'weixin get get_cookies()'
    for i in range(2): 
        print '===============',i
        url = 'http://weixin.sogou.com/weixin?query=%s'%\
                random.choice('abcdefghijklmnopqrstuvwxyz')
        t = requests.get(url=url)
        text = t.cookies
        # print text
        cookies_list=re.findall(r"(?<=<Cookie\s).+?=.+?(?=\sfor)",
                                str(text))
        cookie = {
            'ABTEST':'7|1430810607|v1',
            'IPLOC':'CN4201',
            'PHPSESSID':'bjbvji1318u2mi6smp6g6tba46',
            'SNUID':'C23CCCD8AFAABAFE3AACCBF8AF541E29',
            'SUID':'6C9262776A20900A0000000055486FF4',
            'SUID':'6C9262777E23900A0000000055486FF4',
            'SUIR':'1430810612',
            'SUV':'00E87B617762926C55487004EB218696'
        }

        # cookie = {
        #     'ABTEST':'0|1430818728|v1',
        #     'IPLOC':'CN4201',
        #     'PHPSESSID':'sp4sfq7u8ns6sotmlnedcm0v57',
        #     'SNUID':'F30DFDD79FA5B5F2D22405A1A0AD170F',
        #     'SUID':'6C9262776F1C920A0000000055488FA8',
        #     'SUID':'6C9262774C1C920A0000000055488FA9',
        #     'SUIR':'1430818729',
        #     'SUV':'00AC7B5C7762926C55488FA0C59A5426'
        # }

        cookie = {
            'ABTEST':'0|1430900634|v1',
            'IPLOC':'CN4201',
            'PHPSESSID':'jk988nfggq1vlmst38q84tubs7',
            'SNUID':'53ECE208807A6AE50483D22F80DEA976',
            'SUID':'D39362776A20900A000000005549CF9A',
            'SUID':'D39362771524900A000000005549CFB0',
            'SUIR':'53ECE208807A6AE50483D22F80DEA976',
            'SUV':'00647D92776293D35549CFB042FDE894'
        }
        for item in cookies_list:
            item = item.split('=')
            cookie[item[0]] = item[1]
        
        if cookie.get('SNUID'):
            print 'cun zai --------'
            UT = int(time.time())-1
            cookie['SUIR'] = str(UT)
            cookie['SUV'] = str(UT*1000000+random.randint(1, 1000))
            cookies.append(cookie)

        else:
            print 'zhao bu dao '
            time.sleep(random.randint(10,30))
            print 'Gets a cookies failure , file:sogou'
            cookies = []
            break
        print cookie
        time.sleep(random.randint(1,8))
    return cookies
# cookies = get_cookies()
# cookie = random.choice(cookies)
# print cookie
print '---------------------'
cookie = {
    'ABTEST':'7|1430810607|v1',
    'IPLOC':'CN4201',
    'PHPSESSID':'bjbvji1318u2mi6smp6g6tba46',
    'SNUID':'C23CCCD8AFAABAFE3AACCBF8AF541E29',
    'SUID':'6C9262776A20900A0000000055486FF4',
    'SUID':'6C9262777E23900A0000000055486FF4',
    'SUIR':'1430810612',
    'SUV':'00E87B617762926C55487004EB218696'
}
# url = 'http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid=oIWsFt-sdJ9DF0dwZ6zs28IoEmt4&repp=1'
# # # url = 'http://weixin.sogou.com/gzh?openid=oIWsFt23c5LqoZ5r4FYYFFAWYtu0'
# aa = requests.get(url,cookies=cookie)
# aa.encoding = 'GBK'
# print aa.text.encode('utf-8')





test = {
    'ABTEST':'0|1430818728|v1',
    'IPLOC':'CN4201',
    'PHPSESSID':'sp4sfq7u8ns6sotmlnedcm0v57',
    'SNUID':'F30DFDD79FA5B5F2D22405A1A0AD170F',
    'SUID':'6C9262776F1C920A0000000055488FA8',
    'SUID':'6C9262774C1C920A0000000055488FA9',
    'SUIR':'1430818729',
    'SUV':'00AC7B5C7762926C55488FA0C59A5426'
}


url = 'http://www.pm25s.com/wuhan.html'
a = requests.get(url)
print a.text.encode('utf-8')