# -*- coding: utf-8 -*-
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory
from settings import CASSA_CONN_STR

class CassandraClient(object):
    session = None
    conn = None

    def __init__(self):
        self.conn = {
            'hosts': CASSA_CONN_STR['hosts'],
            'port': CASSA_CONN_STR['port'],
            'username': '',
            'password': ''
        }

    def connect(self, keyspace):
        cluster = Cluster(contact_points=self.conn['hosts'].split(','),
            port=self.conn['port'], auth_provider=PlainTextAuthProvider(
            username=self.conn['username'], password=self.conn['password']))
        metadata = cluster.metadata
        self.session = cluster.connect(keyspace)

    def close(self):
        self.session.cluster.shutdown()
        self.session.shutdown()


def get_session(keyspace):
    client = CassandraClient()
    client.connect(keyspace)
    return client.session


def close_client(client):
    client.close()


if __name__ == '__main__':
    pass
  #  print CASSA_CONN_STR
    # client = get_client("zjld")
    # session = get_session()
    # close_client(client)
