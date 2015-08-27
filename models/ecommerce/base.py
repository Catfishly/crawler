# -*- coding: utf-8 -*-
import logging
import copy
from uuid import uuid1
from datetime import datetime
from utils.datetimeutil import unix_time
from utils.datetimeutil import unix_time
from models.modelbase import ModelBase


_LOGGER = logging.getLogger("ecommerceimport")


class ContentModel(ModelBase):

    TYPE = "base.content"
    FIELDS = {
        "id": uuid1(),
        "source": u"",
        "source_level": {},
        "first_level": u"",
        "second_level": u"",
        "third_level": u"",
        "fourth_level": u"",
        "fifth_level": u"",
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

    def _import(self):
        dup = self.find_dup()                                                                                             
        if dup:
            self["id"] = dup["id"]

            self.merge(dup)
            if not self.equals(dup):
                self.save()
                return True
                _LOGGER.info("UPDATED MODEL - %s", self)
            else:
                _LOGGER.info("SKIPPED MODEL - %s", self)
                return False
        else:
            self.save()
            _LOGGER.info("INSERTED MODEL - %s", self)
            return True

    def save(self):
        id = self.get("id")
        session = self.session()
        if not id:
            self["id"] = self.new_id()

        querystr = ""
        for key in self.FIELDS.keys():
            querystr += "%(" + key + ")s,"

        querystr = "INSERT INTO " + Cluster['table'] + \
            str(tuple(self.FIELDS.keys())).replace("'", "") + \
            "VALUES" + "(" + querystr[:-1] + ")"

        session.execute(querystr, self)

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
