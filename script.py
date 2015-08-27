# -*- coding: utf-8 -*-
import sys
from settings import CRAWLER_PID


def crawlerservice(command):
    from crawlerservice import CrawlerService
    service = CrawlerService(CRAWLER_PID)
    if command == "start":
        service.start()
    elif command == "stop":
        service.stop()
    elif command == "restart":
        service.restart()
    elif command == "status":
        service.status()


if __name__ == '__main__':
	crawlerservice(sys.argv[1])