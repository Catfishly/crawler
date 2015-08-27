#!/usr/bin/python
#-*- encoding:utf-8 -*-
from urllib import quote ,unquote
import requests
# url = 'http://api.weibo.cn/2/guest/login?v_f=2&c=android&wm=2468_1001&ua=HUAWEI-HUAWEI%20T8950__weibo__5.2.0__android__android4.0.4&oldwm=2468_1001&from=1052095010&lang=zh_CN&skin=default&i=5c7d1a1'
# datas = {
#     'did':'006997cad1bdce0960777445e8b8fed2',
#     'device_id': '006997cad1bdce0960777445e8b8fed2516bef94',
#     'device_name': 'HUAWEI-HUAWEI+T8950',
#     'checktoken': '145017482e276309764c38987d3ae67',
#     'imei': '867495011754326'
# }
# con =  requests.post(url, data=datas)
# print con.text.encode('utf-8')

data = requests.get("http://www.baidu.com")
print data

#"{"uid":"1001979296366","gsid":"4wkmda923WBtPcv1v5vMS15OcAo5U","token":"_2AkMieYqCf8NhqwJRmPkcy2LgZYt0zA7EiebDAH_sJxI3Hi4d7DxvjqeU3odrp28qN_KtaGwVSt1x"}"
#"{"uid":"1001979296366","gsid":"4wkmda923WBtPcv1v5vMS15OcAo5U","token":"_2AkMieYn9f8NhqwJRmPkcy2LgZYt0zA7EiebDAH_sJxIwHiFP7IycovvXQnlQpx8ttlxYJuJOOm-h"}
#_2A254ILQGDeTxGeRM7lUR8CnKyT2IHXVZdEDOrDV6PUJbrdANLUjtkWoAnN-DujZpmtGh_tC9kQmOb6O2bg..


# url = 'http://api.weibo.cn/2/account/login?uid=1001361546215&wm=3333_2001&i=a02405c&b=0&from=1052093010&checktoken=ba1173331d147ae8718386e7be706018&c=iphone&v_p=18&skin=default&v_f=1&did=19d36983946c6d325dcc671ee64f355d&lang=zh_CN&ua=iPhone6,2__weibo__5.2.0__iphone__os8.1.1'



# datas = {
#     'p':'GdQ3L8X2Z0aek3NRYv7UX42YKx2J5L0r%2FajxFEDLbsKHRQIQJLok8A6kAcVpfEtTrgjEuqITv44UIDZbrz%2FSoGzV2lrGdMrj28p6e2KTzqF8VjV0n0W54q%2FS0jKJr3MX%2BGwN5NpNstg%2FHRuQE9mKp%2BlRpAhZgGAuS56ZB6iEw0U%3D',
#     'checktoken': 'ba1173331d147ae8718386e7be706018',
#     'uicode': '10000058',
#     'guestid': '1001361546215',
#     's': 'ef79a7a4',
#     'flag': 1,
#     'imei': 'b0ffb799747a6d4a3ac0b597c868725c401838b8',
#     'device_name': 'E2%80%9Csnail%E2%80%9D%E7%9A%84%20iPhone',
#     'did': '19d36983946c6d325dcc671ee64f355d',
#     'getcookie': 1,
#     'u': '15871794193',
#     'device_id': '19d36983946c6d325dcc671ee64f355d23bb1e3d',
#     'aid': '01AtnqUHpEiTaIRvX6K9XdDti9nA6z85r8P8e401fBpn63kqQ.'
# }
# con =  requests.post(url, data=datas)
# print con.text.encode('utf-8')

