import handler
import datetime
from pymongo import MongoClient
from scheduler.crawler import Status
from settings import MONGO_CONN_STR, CASSA_CONN_STR

class InvalidType(Exception):
    pass

class ErrorHandler(handler.Handler):
    _conn = MongoClient(MONGO_CONN_STR)
    _db = _conn["crawler"]
    NO_TASK = 1
    def __init__(self):
        #super(handler.Handler, self).__init__(task)
        #self.task = task
        pass

    def handle(self): 
        raise InvalidType()

    def updateError(self):
        obj_id = self.task.obj_id
        ErrorHandler._db['ecommerce'].update({"_id": obj_id}, 
                                             {"$set": {"status": Status.Failed,
                                                       'update_time': datetime.datetime.utcnow()}})
