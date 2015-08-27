#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
root_mod = '/home/xxguo/Project/crawler'
sys.path.append(root_mod)

import logging
import time
import datetime
from pymongo import MongoClient
from multiprocessing import Process, Queue, Value
from handler import HandlerFactory
from message import Message
from scheduler.crawler import Crawler, Status, Scheduler
from utils import get_exception_info
from settings import MONGO_CONN_STR, CASSA_CONN_STR

logger = logging.getLogger("ecommercecrawler")


class WorkProcess(Process):

    _conn = MongoClient(MONGO_CONN_STR)
    _db = _conn["crawler"]

    def __init__(self, taskqueue, msgqueue):
        super(WorkProcess, self).__init__()
        self.taskqueue = taskqueue
        self.msgqueue  = msgqueue
        self.runValue = Value('i', 1)
        self.ctask = None


    def run(self):
        while True:
            if not self.runValue.value:
                print "%s stops" % self.name
                break
            self.signalget()
            start_t = time.time()
            self.ctask = self.taskqueue.get()
            if self.ctask.empty:
                time.sleep(10)
                continue
            end_t = time.time()
            self.log_wait_task(end_t - start_t)
            self.log_get_task()
            start_t = time.time()

            c = Crawler().create(self.ctask.type, self.ctask.key, self.ctask.data)
            if c:
                try:
                    c.crawl()
                    success = True
                    logger.info("CRAWL SUCCEED - <%s> %s" % (self.taskqueue.queueid, c))
                    end_t = time.time()
                    self.log_done_task(end_t - start_t)
                except Exception:
                    msg = get_exception_info()
                    success = False
                    logger.error("CRAWL FAILED - <%s> %s, %s" % (self.taskqueue.queueid, c, msg))
            else:
                logger.error("CRAWL FAILED - <%s> %s" % (self.taskqueue.queueid, self.ctask))
                success = False

            Scheduler.finish(self.ctask.type, self.ctask.key, c.data if c else {}, success)


    def stop(self):
        self.runValue.value = 0


    def signalget(self):
        mdata = {'queueid': self.taskqueue.queueid}
        mtype = Message.REQUEST_GET
        self.sendmsg(mtype, mdata)


    def log_get_task(self):
        form = "child process %s get a task %s from task queue %s"
        qid = self.taskqueue.queueid
        tid =  self.ctask._id
        text = form % (self.pid, tid, qid)
        self._log(text)

    def log_done_task(self, costs):
        form = "child process %s done a task %s costing %ss"
        tid =  self.ctask._id
        text = form % (self.pid, tid, costs)
        self._log(text)

    def log_fail_task(self):
        form = "child process %s done a task %s failed"
        tid =  self.ctask._id
        text = form % (self.pid, tid)
        self._log(text)
    
    def log_wait_task(self, costs):
        form = "child process %s wait a task costing %ss"
        text = form % (self.pid, costs)
        self._log(text)

    def log_no_task(self):
        form = "child process %s start to spleep 5 seconds for no task"
        text = form % (self.pid)
        self._log(text)
        
    def _log(self, text):
        mdata = {}   
        mdata = {'text': text}
        mtype = Message.REQUEST_LOG
        self.sendmsg(mtype, mdata)
    

    def sendmsg(self, mtype, mdata):
        msg = Message(mtype, mdata)
        self.msgqueue.put(msg)


if __name__ == "__main__":
    """
    tasks = Queue()
    for i in range(10):
        tasks.put(Task(i))
    main = Queue()
    p = WorkProcess(tasks)
    p.start()
    print "main process left"
    # """
    # import uuid
    # data = {
    #   #  'source': 'gome',
    #     "priorcategory" : ["冰箱 洗衣机 空调","冰箱/冷柜","冰箱"],
    #     "presentcategory": ["冰箱 洗衣机 空调","冰箱/冷柜","冰箱"],
    #     "uuid": uuid.uuid1()
    # }
#    c = Crawler().create('ecommerce.gome.goodslist', 'cat10000054', {"priorcategory" : ["教育音像"]})
    # c = Crawler().create('ecommerce.jd.goodscomment', '272765', data)
    # keys = 'http://list.yhd.com/c32159-0-0/'
    # c = Crawler().create('ecommerce.yhd.goodslist', keys, data)
    # print c
 #   c.crawl()


    keys = '7天无理由退货正式写入新《消费者权益保护法》'
    c = Crawler().create('zjld.baidu.newstitle', keys, data={})
    print c.crawl()
