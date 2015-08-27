# -*- coding: utf-8 -*-
import logging
import copy
import time
from uuid import uuid1
from datetime import datetime
from utils.datetimeutil import unix_time
from models.modelbase import ModelBase
from db.cassandra.executor import CassandraQueryApi


_LOGGER = logging.getLogger("zjldimport")


class ContentModel(ModelBase):

    TYPE = "base.content"
    FIELDS = {
        "id": uuid1(),
        "source": u"",
        "origin_source": u"",     
        "type": u"",
        "pubtime": datetime.utcfromtimestamp(0),
        "crtime": datetime.now(),
        "crtime_int": int(time.time() * 1000000),
        "province": u"",
        "city": u"",
        "district": u"",
        "comment": {}
    }

    def __init__(self, dct={}, authority=None):
        if not isinstance(dct, dict):
            raise TypeError
        for key in self.FIELDS.iterkeys():
            '''
            New model id is None, do not set id field.
            Old model id is not None, should set id field.
            '''
            if key == "id" and dct.get(key) is None:
                continue
            self.set_field(key, dct.get(key))

    def __setitem__(self, key, value):
        return self.set_field(key, value)

    def set_field(self, field, value):
        ret = super(ContentModel, self).__setitem__(field, value)

        if (value is None) or self.is_empty(field):
            return ret

    def is_empty(self, field):
        defvalue = self.FIELDS[field]
        if isinstance(defvalue, bool):
            return False
        if field in ["price", "original_price"]:
            return False

        return self[field] == defvalue

    def _import_cassandra(self, keyspace, column_family):
        dup = self.find_dup()
        if dup:
            self["id"] = dup["id"]

            self.merge(dup)
            if not self.equals(dup):
                self.save_cassandra(keyspace, column_family)
                return True
                _LOGGER.info("UPDATED CASSANDRA MODEL - %s", self)
            else:
                _LOGGER.info("SKIPPED CASSANDRA MODEL - %s", self)
                return False
        else:
            self.save_cassandra(keyspace, column_family)
            _LOGGER.info("INSERTED CASSANDRA MODEL - %s", self)
            return True

    def save_cassandra(self, keyspace, column_family):
        self["id"] = self.get("id") if self.get("id") else self.new_id()

        cql = "INSERT INTO %s (%s) VALUES (%s)" \
                % (
                    column_family,
                    reduce(
                        lambda x, y: x + ", " + y, 
                        self.keys()
                    ),
                    reduce(
                        lambda x, y: x + ", " + y, 
                        ["%s" for x in self.keys()]
                    )
                )
        CassandraQueryApi(keyspace).save(cql, self.values())
        return self


    def new_id(self):
        return uuid1()

    def on_import(self):
        self._import()

    def export(self):
        dct = dict(self)
        dct["id"] = dct.pop("id")
        return dct

    def find_dup(self):
        raise NotImplemented

    def merge(self, item):
        '''
        item: existing item in database
        '''
        for field in self.FIELDS.iterkeys():
            if field in ["id"]:
                continue

            overwrite = True

            value = self.merge_value(field, item[field], overwrite)
            self.set_field(field, value)

    def merge_value(self, field, value, overwrite):
        '''
        value: existing value, ***DO NOT MODIFY***
        overwrite: whether should value overwrite self[field]
        '''
        return value if overwrite else self[field]

    def equals(self, item):
        if self.__class__ != item.__class__:
            return False
        for k in self.FIELDS.keys():
            if k not in ["_id", "created", "updated"]:  # TODO: authorities
                if isinstance(self[k], datetime):
                    # drop precise
                    if unix_time(self[k]) != unix_time(item[k]):
                        return False
                elif self[k] != item[k]:
                    return False
        return True

    def __unicode__(self):
        return u"%s(%s)" % (self.TYPE, self['id'])

    def __str__(self):
        return "%s(%s)" % (self.TYPE, self['id'])
