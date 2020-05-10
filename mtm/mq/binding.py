from . import rabbit_registry
from .queue import RabbitQueue
from .exchange import TopicExchange
import logging


log = logging.getLogger(__name__)


class Binding:
    def __init__(self, queue, exchange):
        self._queue = RabbitQueue(queue)
        self._exchange = TopicExchange(exchange)
        rabbit_registry.register(self)

    @property
    def exchange(self):
        return self._exchange

    @property
    def queue(self):
        return self._queue

    @property
    def is_consumer(self):
        return isinstance(self, Consumer)

    def __str__(self):
        return "<Binding(%s)> %s:%s" % (
            self.__class__.__qualname__.lower(),
            self.exchange,
            self.queue,
        )

    def __repr__(self):
        return str(self)


class Consumer(Binding):
    def __init__(self, binding_key, queue, exchange):
        super().__init__(queue, exchange)
        self.queue.binding_key = binding_key

    def __call__(self):
        def _f(cb):
            self._queue.register_on_message(cb)

        return _f

    def consumer_tag(self):
        return self.queue.consumer_tag


class Producer(Binding):
    def __init__(self, queue, exchange):
        super().__init__(queue, exchange)
        self._channel = None

    def attach_channel(self, ch):
        self._channel = ch

    @property
    def channel(self):
        return self._channel

    def publish_json(self, routing_key, message):
        self.channel.publish_json(self.exchange, routing_key, message)

    def ack_msg(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)


# class Listener(abc.ABC):
#     def __init__(self, queue_name, exchange_name):
#         self._queue = RabbitQueue(queue_name)
#         self._exchange = TopicExchange(exchange_name)
#         rabbit_registry.register(self)
#
#     @property
#     def exchange(self):
#         return self._exchange
#
#     @property
#     def queue(self):
#         return self._queue
#
#     @property
#     def is_consumer(self):
#         return True
#
#     @abc.abstractmethod
#     def on_message(self, channel, basic_deliver, properties, body):
#         pass
#
#     def listen_on(self, binding_key):
#         self.queue.binding_key = binding_key
