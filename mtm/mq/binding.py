from .queue import RabbitQueue
from .exchange import TopicExchange, default_exchange
import logging

log = logging.getLogger(__name__)


class Binding:
    def __init__(self, queue, exchange):
        self._queue = RabbitQueue(queue)
        if exchange == "default":
            self._exchange = default_exchange
        else:
            self._exchange = TopicExchange(exchange)
        self._channel = None
        self._is_consumer = False

    @property
    def exchange(self):
        return self._exchange

    @property
    def queue(self):
        return self._queue

    def set_binding_key(self, binding_key):
        self._is_consumer = True
        self._queue.binding_key = binding_key

    @property
    def is_consumer(self):
        return self._is_consumer

    def attach_channel(self, ch):
        self._channel = ch

    @property
    def channel(self):
        return self._channel

    def __str__(self):
        return "<Binding(%s)> %s:%s" % (
            self.__class__.__qualname__.lower(),
            self.exchange,
            self.queue,
        )

    def __repr__(self):
        return str(self)
