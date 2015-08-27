# -*- coding: utf-8 -*-

from db.redis.connection import get_instance


class RedisQueryApi(object):
    """Redis Query Api"""
    instance = None

    def __init__(self):
        self.instance = get_instance()

    def set(self, name, key, value):
        self.instance.set(key, value)

    def get(self, name, key):
        return self.instance.get(key)

    def hexists(self, name, key):
        return self.instance.hexists(name, key)

    def expireat(self, name, time):
        print name,time
        self.instance.expireat(name, time)

    def SADD(self, name, key):
        self.instance.sadd(name, key)

    def HMSET(self, name, values):
        self.instance.hmset(name, values)

