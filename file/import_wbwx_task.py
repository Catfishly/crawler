#!/usr/bin/python
#coding=utf-8

from xlutils.copy import copy
import xlrd
import sys
import MySQLdb
reload(sys)
sys.setdefaultencoding( "utf-8" )

# def read_task():
#     bk = xlrd.open_workbook('weixin.xls')
#     sh = bk.sheet_by_name('Sheet1')
#     nrows = sh.nrows
#     ncols = sh.ncols
#     for i in xrange(1,nrows):
#         author = sh.cell_value(i,0).strip()
#         province = sh.cell_value(i,1).strip()
#         city = sh.cell_value(i,2).strip()
#         district = sh.cell_value(i,3).strip()
#         key = sh.cell_value(i,6).strip()
#         save_mysql(author)
#         print author

# def save_mysql(name):
#     db = MySQLdb.connect(host='192.168.1.101', 
#             user='root', passwd='password', 
#             db='yqj', charset='utf8')
#     sql = "insert into weixinpublisher(photo,publisher,brief) values('%s','%s','%s')"%('kong',name,'kong')
#     cursor = db.cursor()
#     cursor.execute(sql)
#     db.commit()
#     db.close()

def read_task():
    # bk = xlrd.open_workbook('event.xls')
    bk = xlrd.open_workbook('newyuqing.xls')
    sh = bk.sheet_by_name('Sheet1')
    nrows = sh.nrows
    ncols = sh.ncols
    # for i in xrange(1,nrows):
    #     author = sh.cell_value(i,0).strip()
    #     # province = sh.cell_value(i,1).strip()
    #     # city = sh.cell_value(i,2).strip()
    #     # district = sh.cell_value(i,3).strip()
    #     # key = sh.cell_value(i,6).strip()
    #     save_mysql(author)
    #     print author

def save_mysql(name):
    db = MySQLdb.connect(host='192.168.1.101', 
            user='root', passwd='password', 
            db='yqj', charset='utf8')
    sql = "insert into topic(title,abstract,area_id,source) values('%s','%s',%s,'%s')"%(name,'kong',0,'baidu')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close()
if __name__ == '__main__':
    read_task()