# -*- coding: utf-8 -*-
import MySQLdb
from peewee import *

class MySQLClient(object):
    """docstring for MySQL"""
    def __init__(self, conf={}):
        conf  = {
            'host': '192.168.1.101',
            'port': '3306',
            'user': 'root',
            'passwd': 'password',
            'db': 'yqj'
        }
        self.conf = conf

    def connect(self):
        db = MySQLdb.connect(host=self.conf["host"], user=self.conf["user"],
            passwd=self.conf["passwd"], db=self.conf["db"])
        return db.cursor()

    def db(self):
        return MySQLDatabase(self.conf["db"], 
            user=self.conf["user"], passwd=self.conf["passwd"])


def get_cursor():
    return MySQLClient().connect()


def mysql_db():
    return MySQLClient().db()


if __name__ == '__main__':
    get_cursor()