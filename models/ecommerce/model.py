# -*- coding: utf-8 -*-
from datetime import datetime
from uuid import uuid1
from base import ContentModel
from db.cassandra.executor import CassandraQueryApi
from utils.text import clean_list, clean_text, clean_url, \
    clean_paragraph, is_uuid


class EcBasicModel(ContentModel):

    TYPE = "ecommerce.basic"

    FIELDS = {
        "source_id": u"",
        "title": u"",
        "adword": u"",
        "version": u"",
        "original_price": 0.0,
        "history_price": {},
        "price": 0.0,
        "score": 0,
        "summary": {},
        "address": u"",
        "status": 0,
    }
    INDEXES = [
        {"key": [("source", 1), ("source_id", 1)], "unique": True},
    ]

    def __init__(self, dct={}):
        super(EcBasicModel, self).__init__(dct)

    def find_dup(self):
        dup = []
        if self.get('id'):
            pass
        if self.get('source_id'):
            cql = """SELECT * FROM %s WHERE source_id='%s' LIMIT 1""" \
                % (self.TYPE.split(".")[1], self['source_id'])
            dup = CassandraQueryApi().find(cql)

        return self.wrap(dup[0] if dup else None)

    def clean_value(self, field, value):
        return value  # leave original value

    def on_import(self):
        if self['source'] and self['source_id']:
            self._import()


class EcDetailModel(ContentModel):

    TYPE = "ecommerce.detail"

    FIELDS = {
        "source_id": u"",
        "name": u"",
        "brand": u"",
        "images": [],
        "summary": {},
        "intro_img": [],
        "introduce": {},
        "summary": {},
        "extra_info": {},
        "recommend": [],
        "popular": [],
        "address": u"",
        "status": 0,
    }

    INDEXES = [
        {"key": [("title", 1)]},
        {"key": [("source", 1), ("updated", 1)]},
    ]

    def __init__(self, dct={}):
        super(EcDetailModel, self).__init__(dct)

    def find_dup(self):
        dup = None
        if self.get('id'):
            pass

        return self.wrap(dup)

    def on_import(self):
        if self['source'] and self['source_id']:
            self._import()


class EcCommentModel(ContentModel):

    TYPE = "ecommerce.comment"

    FIELDS = {
        "eid": uuid1(),
        "source_id": u"",
        "comment_id": u"",
        "score": 0.0,
        "pubtime": datetime.utcfromtimestamp(0),
        "buytime": datetime.utcfromtimestamp(0),
        "useful": 0,
        "reply": 0,
        "user_id": u"",
        "tags": [],
        "content": u"",
        "show_pic": []
    }

    INDEXES = [
        {"key": [("user_id", 1)]},
        {"key": [("comment_id", 1)]},
    ]

    def __init__(self, dct={}):
        super(EcCommentModel, self).__init__(dct)

    def find_dup(self):
        dup = None
        if self.get('id'):
            # dup = self.columnfamily().get(self['id'])
            pass
        if self.get('comment_id'):
            cql = """SELECT * FROM %s WHERE comment_id='%s' LIMIT 1""" \
                % (self.TYPE.split(".")[1], self['comment_id'])
            dup = CassandraQueryApi().find(cql)

        return self.wrap(dup[0] if dup else None)

    def on_import(self):
        if self['source'] and self['source_id']:
        #    return self._import()
            keyspace, column_family = self.TYPE.split(".")
            return self._import_cassandra(keyspace=keyspace,
                 column_family=column_family)
