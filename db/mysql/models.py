# -*- coding: utf-8 -*-

from peewee import *
from db.mysql.connection import mysql_db


class BaseModel(Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = mysql_db()

class Weixin(BaseModel):
    """Weixin Model"""
    author = CharField()
    title = CharField()
    url = CharField()
    content = TextField()
    origin_source = CharField()
    source = CharField()
    website_type = CharField()
    pubtime = DateTimeField()
    area_id = IntegerField()
    publisher_id = IntegerField()


class Weibo(BaseModel):
    """Weibo Model"""
    author = CharField()
    title = CharField()
    url = CharField()
    content = TextField()
    origin_source = CharField()
    source = CharField()
    website_type = CharField()
    pubtime = DateTimeField()
    area_id = IntegerField()
    publisher_id = IntegerField()

