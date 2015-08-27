import logging
import os
from workProcess import WorkProcess
from multiprocessing import Value, Queue
from taskContainer import TaskContainer, TaskPriorityQueue
from strategy import SimpleAssignStrategy
from message import Message



class  ProcessPool:
    def __init__(self, strategy, process_num):
        self.mainqueue = Queue()
        self.process = {}
        self.strategy = strategy(self.mainqueue)

        for i in range(process_num):
            self.add_process()


    def add_process(self):
        queueid = TaskContainer().getNewId()
        queue = TaskPriorityQueue(queueid)
        TaskContainer().addQueue(queue)
        p = WorkProcess(queue, self.mainqueue)
        self.process[p] = queueid



    def start(self):
        self.strategy.assignTask()
        print TaskContainer().getAllSize()
      #  return
        for p in self.process:
            p.start()

        while True:
            msg = self.mainqueue.get()
            mtype = msg.gettype()
            mdata = msg.getdata()

            if mtype == Message.REQUEST_GET:
                TaskContainer().putpipe(mdata['queueid'])
                self.update_proc()
                self.strategy.assignTask()
            elif mtype == Message.REQUEST_LOG:
                text = mdata['text']
                logging.debug(text)

    def update_proc(self):
        for p in self.process.keys():
            if not p.is_alive:
                self.log_died_process(p.pip)
                newproc = WorkProcess(self.process[p])
                self.process[newproc] = self.process[p]
                self.process.pop(p)

    def stop(self):
        for p in self.process:
            p.stop()

    def log_died_process(self, child_pid):
        mformat = "child process %s died"
        text = mformat % child_pid
        logging.debug(text)

def log_init():
    try:
        os.mkdir('log')
    except os.OSError:
        pass
    logging.basicConfig(format='%(asctime)s  %(message)s', filename='log/process.log', level=logging.DEBUG)


if __name__ == "__main__":
    #log_init()
    stgy = SimpleAssignStrategy
    pool = ProcessPool(stgy, 4)
  #  pool.start()
