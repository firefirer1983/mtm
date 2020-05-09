from . import binding_registry
from .queue import RabbitQueue
from .exchange import TopicExchange
import logging

log = logging.getLogger(__name__)


class Binding:
    def __init__(self, queue_name, exchange_name):
        self._queue = RabbitQueue(queue_name)
        self._exchange = TopicExchange(exchange_name)
        binding_registry.append(self)

    @property
    def exchange(self):
        return self._exchange

    @property
    def queue(self):
        return self._queue

    @property
    def is_consumer(self):
        return isinstance(self, Consumer)


class Consumer(Binding):
    def __init__(self, queue_name, exchange_name):
        super().__init__(queue_name, exchange_name)

    def listen_on(self, binding_key):
        self._queue.binding_key = binding_key

        def _f(cb):
            self._queue.register_on_message(cb)

        return _f

    def __call__(self, binding_key):
        self._queue.binding_key = binding_key

        def _f(cb):
            self._queue.register_on_message(cb)

        return _f


class Producer(Binding):
    def __init__(self, queue_name, exchange_name):
        super().__init__(queue_name, exchange_name)

