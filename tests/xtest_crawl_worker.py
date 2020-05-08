import sys
import logging
from os import path
sys.path.append(path.join(path.dirname(__file__), ".."))
from mtm.crawl_worker import CrawlWorker

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    CrawlWorker().run()
