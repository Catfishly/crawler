# -*- coding: utf-8 -*-
from uuid import uuid1
import time
from datetime import datetime
from base import ContentModel
from db.cassandra.executor import CassandraQueryApi
from db.redis.executor import RedisQueryApi

class WeiboArticleModel(ContentModel):
    """docstring for WeiboArticleModel"""

    TYPE = "zjld.weibo"

    FIELDS = {
        "id": uuid1(),
        "author": u"",
        "title": u"",
        "subtitle": [],
        "content": u"",
        "url": u"",
        "imgurl":[],
        "source": u"",
        "origin_source": u"",
        "pubtime": datetime.utcfromtimestamp(0),
        "crtime": datetime.now(),
        "publisher": u"",
        "province": u"",
        "city": u"",
        "district": u"",
    }

    def __init__(self, dct={}):
        super(WeiboArticleModel, self).__init__(dct)

    def find_dup(self):
        dup = []
        if self.get('url'):
            cql = """SELECT * FROM %s WHERE url='%s' LIMIT 1""" \
                % (self.TYPE.split(".")[1], self['url'])
            dup = CassandraQueryApi(self.TYPE.split(".")[0]).find(cql)

        return self.wrap(dup[0] if dup else None)

    def clean_value(self, field, value):
        return value  # leave original value

    def on_import(self):
        if self['source'] and self['url']:
            keyspace, column_family = self.TYPE.split(".")
            return self._import_cassandra(keyspace=keyspace,
                 column_family=column_family)


class WeiboHotModel(ContentModel):
    """docstring for WeiboHotModel"""

    TYPE = "zjld.weibohot"

    FIELDS = {
        "id": "",
        "reposts": 0,
        "comments": 0,
        "likes": 0,
        "expire": 604800
    }

    def __init__(self, dct={}):
        super(WeiboHotModel, self).__init__(dct)

    def find_dup(self):
        dup = []
        if self.get('id'):
            dup = RedisQueryApi().get(self.TYPE.split(".")[1], self["id"])
        return self.wrap(eval(dup) if dup else None)

    def clean_value(self, field, value):
        return value  # leave original value

    def on_import(self):
        if self['id']:
            self._import_redis(name=self.TYPE.split(".")[1])
            