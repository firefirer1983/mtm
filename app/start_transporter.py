import os
import sys
from os import path
import logging

sys.path.append(path.join(path.dirname(__file__), ".."))
from mtm.transporter import Transporter

log = logging.getLogger(__file__)

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
amqp_url = os.environ.get("amqp_url", "amqp://guest:guest@localhost:5672/%2F")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    Transporter(amqp_url).run()
