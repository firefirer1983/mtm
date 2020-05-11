from .queue import RabbitQueue
from .exchange import TopicExchange
import logging


log = logging.getLogger(__name__)


class Binding:
    def __init__(self, queue, exchange):
        self._queue = RabbitQueue(queue)
        self._exchange = TopicExchange(exchange)
        self._channel = None
        self._is_consumer = False
        rabbit_registry.register(self)

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

    def register_on_message_callback(self, cb):
        return self._queue.register_on_message_callback(cb)

    def __str__(self):
        return "<Binding(%s)> %s:%s" % (
            self.__class__.__qualname__.lower(),
            self.exchange,
            self.queue,
        )

    def __repr__(self):
        return str(self)


class RabbitRegistry:
    def __init__(self):
        self._bindings = set()

    def register(self, b):
        self._bindings.add(b)

    def unregister(self, bindings):
        self._bindings.remove(bindings)

    def list_bindings(self):
        return list(self._bindings)


rabbit_registry = RabbitRegistry()
