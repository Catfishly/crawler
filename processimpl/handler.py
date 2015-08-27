from abc import ABCMeta, abstractmethod
import time


class HandlerFactory(object):
    @staticmethod
    def makeHandler(task):
        return testHandler(task)


class Handler(object):
    __metaclass__ = ABCMeta

    def __init__(self, task):
        self.task = task


    @abstractmethod
    def handle(self):
        pass


    @abstractmethod
    def updateError(self):
        pass


import random
class testHandler(Handler):
    def __init__(self, task):
        super(testHandler, self).__init__(task)


    def handle(self):
        time.sleep(1)
        #assert self.task.taskid % 2 == 0
        print "process a task %s" % self.task.taskid


    def updateError(self):
        #print "process a task %s failed" % self.task.taskid
        pass



if __name__ == "__main__":
    handl = HandleTask(1)
