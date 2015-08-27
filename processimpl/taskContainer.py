import random
import heapq
from abc import ABCMeta, abstractmethod
from multiprocessing import Pipe

from message import Message
from singleton import singleton
from workProcess import WorkProcess
from multiprocessing import Queue


class Task:
    def __init__(self, data):
        self.empty = False
        for k, v in data.items():
            setattr(self, k, v)
    """        
    def __init__(self, taskid, key, crawl_type, data, priority):
        self.taskid = taskid
        self.type = crawl_type
        self.priority = priority
        self.data = data
        self.key = key
    """


class TaskQueue(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, queueid):
        self.rpipe, self.wpipe = Pipe(False)
        self.queueid = queueid

    def put(self, task):
        self._queuepush(task)

    def get(self):
        task = self.rpipe.recv()
        return task


    def putpipe(self):
        """
        if no task offered, we send a empty task to notify child process
        """
        task = None
        try:
            task = self._queuepop()
        except:
            task = Task({'empty': True})
        self.wpipe.send(task)

    @abstractmethod
    def qSize(self):
        pass

    @abstractmethod
    def _queuepush(self, task):
        pass

    @abstractmethod
    def _queuepop(self):
        pass



class TaskPriorityQueue(TaskQueue):
    def __init__(self, queueid):
        super(TaskPriorityQueue, self).__init__(queueid)
        self.queue = []

    def _queuepush(self, task):
        heapq.heappush(self.queue, (task.priority, task))

    def _queuepop(self):
        priority, task = heapq.heappop(self.queue)
        return task

    def qSize(self):
        return len(self.queue)

    def getprioritysize(self, priority):
        f = lambda x : 1 if x.priority == priority else 0
        return sum(map(self.queue, f))


@singleton
class TaskContainer(object):
    def __init__(self):
        self.queueidDict = {}


    def addQueue(self, newqueue):
        self.queueidDict[newqueue.queueid] = newqueue


    def getAllSize(self):
        f = lambda x: (x[0], x[1].qSize())
        return map(f, self.queueidDict.items())


    def getQueueSize(self, queueId):
        queueSize = self.queueidDict[queueId].qSize()
        return queueSize


    def putTask(self, queueId, task):
        res = self.queueidDict[queueId].put(task)


    def putpipe(self, queueid):
        self.queueidDict[queueid].putpipe()

    def getNewId(self):
        newId = None
        while True:
            newId = random.randint(1, 10000)
            if newId not in self.queueidDict:
                break
        return newId
    

if __name__ == "__main__":
    a = TaskContainer()
    print a.queueidDict


if __name__ == "__main1__":
    mainqueue = Queue()
    queue = TaskPriorityQueue(1)
    for i in range(10):
        queue.put(Task(i, 10 - i))
    for i in range(10):
        queue.put(Task(i, 10 - i))
    queue.putpipe()
    p = WorkProcess(queue, mainqueue)
    p.start()
    while True:
#        print "main process wait for main queue message"
        msg = mainqueue.get()
#        print "main process caught a message"
        if msg.mtype == Message.REQUEST_GET:
            queue.putpipe()
        elif msg.mtype == Message.REQUEST_LOG: 
            print msg.mdata['text']

