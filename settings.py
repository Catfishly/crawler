'''
Settings for crawler

@author: Liuxi Wu
@email : lxwu@shendu.info
'''

import os
import re
from logging import config
from ConfigParser import SafeConfigParser

from utils import rdb
rdb.listen()

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SRC_PATH = os.path.dirname(__file__)
LOGGERS_NAME = ["ecommerceservice", "ecommerceimport", 
    "ecommercecrawler", "zjldimport"]

LOG_BASE = None
DATA_BASE = None

MONGO_CONN_STR = None
CASSA_CONN_STR = None

CRAWLER_PID = None
CRAWLER_PROCESS_MAX_TIME = 3600
CRAWLER_TIMEOUT_DEFAULT = 3600


def _load_config():
    global DEBUG, TEMPLATE_DEBUG, LOG_BASE, DATA_BASE
    global MONGO_CONN_STR, CASSA_CONN_STR, CRAWLER_PID

    SECTION = 'ecommerceservice'

    cp = SafeConfigParser()
    cp.read(os.path.join(SRC_PATH, "conf/ecommerce.cfg"))

    DEBUG = cp.getboolean(SECTION, 'debug')
    TEMPLATE_DEBUG = DEBUG

    LOG_BASE = cp.get(SECTION, 'logs_dir')
    DATA_BASE = cp.get(SECTION, 'data_dir')

    # pid
    CRAWLER_PID = cp.get(SECTION, 'crawler_pid')

    # mongo
    MONGO_CONN_STR = cp.get(SECTION, 'mongo_conn_str')
    cassa_conn_str = cp.get(SECTION, 'cassa_conn_str')

    # cassandra
    CASSA_CONN_STR = re.match(
        r"cassa://(?P<username>.+):(?P<password>.+)@(?P<hosts>.+):(?P<port>\d+)/(?P<keyspace>.+)",
        cassa_conn_str).groupdict()


def get_logging(loggers_name):
    logging = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(levelname)s\t%(asctime)s\t%(message)s'
            },
            'detail': {
                'format': '%(levelname)s\t%(asctime)s\t[%(module)s.%(funcName)s line:%(lineno)d]\t%(message)s',
            },
        }
    }
    handlers = {}
    loggers = {}

    for logger_name in loggers_name:
        handlers[logger_name + "_file"] = {
            'level': 'DEBUG',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(LOG_BASE, logger_name + ".log"),
        }
        handlers[logger_name + "_err_file"] = {
            'level': 'WARN',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(LOG_BASE, logger_name + "_error.log"),
        }
        loggers[logger_name] = {
            'handlers': [logger_name + '_file',  logger_name + '_err_file'],
            'level': 'DEBUG',
            'propagate': True,
        }

    logging['handlers'] = handlers
    logging['loggers'] = loggers

    return logging

_load_config()

LOGGING = get_logging(LOGGERS_NAME)
config.dictConfig(LOGGING)
