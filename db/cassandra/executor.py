# -*- coding: utf-8 -*-

from cassandra.query import dict_factory
from db.cassandra.connection import get_session


_SESSION = None
_SPACELIST = {}
class CassandraQueryApi(object):
    """Cassandra Query API"""
    client = None
    session = None
    keyspace = None

    def __init__(self, keyspace=None):
        if not _SPACELIST.get(keyspace, ''):
            _SPACELIST[keyspace] = get_session(keyspace)
        _SESSION = _SPACELIST[keyspace]
        self.session = _SESSION
        self.session.row_factory = dict_factory

    def find(self, cql):
        """
        cassandra.query.select syntax
        """

        def result():
            result = self.session.execute(cql)
            return result

        return result()

    def save(self, cql, fields):
        """
        cassandra.query.insert syntax
        """

        def insert():
            self.session.execute(cql, fields)

        insert()
