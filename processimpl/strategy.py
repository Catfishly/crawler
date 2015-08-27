import logging
import time
from abc import ABCMeta, abstractmethod
from taskSource import TaskSource
from taskContainer import TaskContainer
from message import Message

class AssignStrategy:
    __metaclass__= ABCMeta

    @abstractmethod
    def assignTask(self):
        pass



class SimpleAssignStrategy(AssignStrategy):
    def __init__(self, mainqueue):
        self.THRESHOLD = 5
        self.MAXQUEUESIZE = 20
        self.mainqueue = mainqueue

    def assignTask(self):
        print TaskContainer().getAllSize()
        for queueId, num in TaskContainer().getAllSize():
            if num <= self.THRESHOLD:
                tasks = TaskSource().getTask(self.MAXQUEUESIZE - num)
                for tk in tasks:
                    TaskContainer().putTask(queueId, tk)
                    mformat = "main process put task %s into queue %s"
                    text = mformat % (tk._id, queueId)
                    self.log_put_task(text)

    def log_put_task(self, text):
        mdata = {}
        mdata['text'] = text
        mtype = Message.REQUEST_LOG
        msg = Message(mtype, mdata)
        self.mainqueue.put(msg)



class CategoryAssignStrategy(AssignStrategy):
    def __init__(self):
        pass
