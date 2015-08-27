# -*- coding: utf-8 -*-
import redis

class RedisClient(object):

    conf = None

    """docstring for RedisClient"""
    def __init__(self):
        self.conf = {
            'host': '192.168.1.202',
            'port': '6379',
            'db': 0
        }

    def connect(self):
        pool = redis.ConnectionPool(host=self.conf['host'],
            port=self.conf['port'], db=self.conf['db'])
        return redis.Redis(connection_pool=pool)


def get_instance():
    return RedisClient().connect()


if __name__ == '__main__':
    get_instance()