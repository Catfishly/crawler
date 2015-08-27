# -*- coding: utf-8 -*-
import copy
from utils.typeutil import convert


class ModelMeta(type):

    def __init__(self, name, bases, dct):
        fields = dct.get('FIELDS', {})
        base = bases[0]
        while base != object:
            for k, v in base.__dict__.get('FIELDS', {}).iteritems():
                fields[k] = v
            base = base.__base__
        dct['FIELDS'] = fields

        indexes = dct.get('INDEXES', [])
        base = bases[0]
        while base != object:
            indexes.extend(base.__dict__.get('INDEXES', []))
            base = base.__base__
        dct['INDEXES'] = indexes

        type.__init__(self, name, bases, dct)


class ModelBase(dict):

    __metaclass__ = ModelMeta

    TYPE = "base"
    FIELDS = {}
    INDEXES = []

    def __init__(self, dct={}):
        if not isinstance(dct, dict):
            raise TypeError
        for key in self.FIELDS.iterkeys():
            self[key] = dct.get(key)

    def __setitem__(self, key, value):
        if key not in self.FIELDS:
            return  # ignore

        t = type(self.FIELDS[key])

        if value is None:
            value = copy.deepcopy(self.FIELDS[key])
        elif not isinstance(value, t):
            value = convert(value, t)
            if value is None:
                raise TypeError

        super(ModelBase, self).__setitem__(key, value)

    def wrap(self, dct):
        if isinstance(dct, ModelBase):
            return dct
        elif isinstance(dct, dict):
            return type(self)(dct)
        else:
            return None

    def find_one(self, query={}, fields=None):
        dct = self.columnfamily().get('id')
        return self.wrap(dct)
