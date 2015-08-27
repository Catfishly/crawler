# -*- coding: utf-8 -*-
import time
import logging
import os
import signal
import sys
from threading import Timer
from utils import get_exception_info
from utils.daemon import Daemon
from scheduler.crawler import _CRAWLER_CONF, CrawlerConf, Crawler, Scheduler
from processimpl.strategy import SimpleAssignStrategy
from processimpl.processPool import ProcessPool
from settings import CRAWLER_PID

logger = logging.getLogger("ecommercecrawler")


class CrawlerService(Daemon):

    def __init__(self, pidfile):
        self._pids = {}
        self._processes = None
        self._crawlers = None
        self._terminating = False
        self._terminated = False
        super(CrawlerService, self).__init__(
            name="crawlerservice", pidfile=pidfile)

    @property
    def processes(self):
        if not self._processes:
            self._processes = dict(_CRAWLER_CONF.processes)
        return self._processes

    @property
    def crawlers(self):
        if not self._crawlers:
            self._crawlers = dict(_CRAWLER_CONF.enabled_crawlers)
        return self._crawlers

    def run(self):
        logger.info("ENTER")
        #Scheduler.check_timeout()
        #signal.signal(signal.SIGTERM, self._term_handler)
        self._init_crawlers()
        #self._init_workers()
        #while not self._terminated:
        #    self._check_crawlers()
        #    self._check_workers()
        #    time.sleep(10)
        stgy = SimpleAssignStrategy
        pool = ProcessPool(stgy, 4)
        pool.start()

    def _term_handler(self, signum, frame):
        self._terminating = True
        for pid in self._pids.keys():
            try:
                os.kill(pid, signal.SIGTERM)
            except:
                pass
        self._pids = {}
        self._terminated = True
        logger.info('SERVICE TERMINATING pid: %s.' % os.getpid())

    def _init_crawlers(self):
        for type, cls in self.crawlers.iteritems():
            cls.init(conf=_CRAWLER_CONF.get_crawler_conf(type))
            logger.info(' CRAWLER INITIALIZED. type(%s)' % type)

    def _init_workers(self):
        for category, count in self.processes.iteritems():
            for i in range(count):
                worker_info = (_service_worker, [category], {})
                pid = self._create_worker(*worker_info)
                if pid:
                    self._pids[pid] = worker_info

    def _create_worker(self, worker, args, kwargs):
        pid = os.fork()
        if not pid:
            worker(*args, **kwargs)
            sys.exit()
        return pid

    def _autorestart_workers(self):
        old_pids = dict(self._pids)
        for pid, worker_info in old_pids.iteritems():
            pid, status = os.waitpid(pid, os.WNOHANG)
            if pid > 0 and (not self._terminating):
                del self._pids[pid]
                new_pid = self._create_worker(*worker_info)
                if new_pid:
                    self._pids[new_pid] = worker_info
                    logger.info(' WORKER RESTART. %s --> %s' % (pid, new_pid))
        logger.info('AUTO RESTART CHECKED. pids: %s' %
                    [x for x in self._pids.keys()])

    """
      In api side, to support add remote command to db .
      In service daemon side, to  load remote command in db and make changes dynamically.
    """

    def _check_crawlers(self):
        # TODO: implement check db changes and update crawler
        pass

    def _check_workers(self):
        # TODO: implement check db changes and update worker process
        self._autorestart_workers()


if __name__ == '__main__':
    service = CrawlerService(CRAWLER_PID)
    service.crawlers
   # service.start()