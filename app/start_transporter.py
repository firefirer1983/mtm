import sys
from os import path
import logging

sys.path.append(path.join(path.dirname(__file__), ".."))
from mtm.transporter import Transporter

log = logging.getLogger(__file__)

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    Transporter().run()
