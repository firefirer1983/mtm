import os
import sys
import logging
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))
from mtm.crawler import Crawler

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
amqp_url = os.environ.get("amqp_url", "amqp://guest:guest@localhost:5672/%2F")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    Crawler(amqp_url).run()
