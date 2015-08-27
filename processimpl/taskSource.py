#import pymongo
import datetime
from pymongo import MongoClient
from collections import deque
from taskContainer import Task
from singleton import singleton
from random import randint
from errorHandler import ErrorHandler
from scheduler.crawler import Status
from settings import MONGO_CONN_STR, CASSA_CONN_STR


@singleton
class TaskSource(object):

    _conn = MongoClient(MONGO_CONN_STR)
    _db = _conn["crawler"]

    def __init__(self):
        self.init_num = 0

        self.FETCHSIZE = 100
        self.taskqueue = deque()
        pass

    def getTask(self, num):
        if len(self.taskqueue) < num:
            fetch_num = num if num > self.FETCHSIZE else self.FETCHSIZE
            self._addTaskFromDb(fetch_num)
        res = []
        if len(self.taskqueue) > num:
            for i in range(num):
                res.append(self.taskqueue.popleft())
        else:
            for i in range(len(self.taskqueue)):
                res.append(self.taskqueue.popleft())
        return res


    def _addTaskFromDb(self, num):
        task = self.searchDatabase(num)
        for i in range(len(task)):
            """
            self.taskqueue.append( Task( task[i]['_id'], 
                                         task[i]['key'],
                                         task[i]['type'],
                                         task[i]['data'],
                                         task[i]['priority']) )
            #print "taskID:", task[i]
            """
            self.taskqueue.append(Task(task[i]))
        self.init_num += len(task)
        
        
    def searchDatabase(self, num):
        task = []
        #ecommerce
        table = TaskSource()._db['zjld']
        priority = table.distinct('priority')
        priority.sort()
        priority.reverse()
        for pri in priority:
            task = self.getCurrentPriTask(task, num, pri)
            if len(task)==num:
                break
        #if len(task) < num:
        #    print "not enough task"
        #print "get task number:", len(task)
        return task

    def getCurrentPriTask(self, task, num, pri):
        table = TaskSource()._db['zjld']
        time = datetime.datetime.utcnow()
        # exce_time = time - datetime.timedelta(days=30)
        # data = table.find({"status": Status.NotStart, "priority": pri, "crtetime":{'$gt':exce_time}})
        data = table.find({"status": Status.NotStart, "priority": pri})
     #   print data.count()
        for doc in data:
            #print doc['nextrun'], time
            if doc['nextrun'] < time:
                task.append(doc)
                table.update({"_id": doc['_id']}, {'$set': {'status': Status.Running, 
                                                            'update_time': datetime.datetime.utcnow()}})
                if len(task) == num:
                    break
        return task

if __name__== "__main__":
    T = TaskSource()
    T.getTask(20)
