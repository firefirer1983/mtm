import abc

from .queue import RabbitQueue
from .exchange import TopicExchange, default_exchange, DefaultExchange
import logging

log = logging.getLogger(__name__)


class Binding(abc.ABC):
    def __init__(self, queue, exchange, binding_key=None):
        self._queue = RabbitQueue(queue)
        if exchange == "default":
            self._exchange = default_exchange
        else:
            self._exchange = TopicExchange(exchange)
        self._channel = None
        self._queue.binding_key = binding_key

    @property
    def exchange(self):
        return self._exchange

    @property
    def queue(self):
        return self._queue

    @property
    def need_binding(self):
        return bool(self._queue.binding_key)

    def attach_channel(self, ch):
        log.info("%s attach channel" % str(self))
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

    @property
    def is_consumer(self):
        return False

    @property
    def is_rpc(self):
        return False


class ConsumerMixin:
    @property
    def is_consumer(self):
        return True


class RpcMixin:
    @property
    def is_rpc(self):
        return True


class ConsumerBinding(Binding, ConsumerMixin):
    def __init__(self, queue, exchange, binding_key):
        super().__init__(queue, exchange, binding_key)


class ProducerBinding(Binding):
    pass


class RpcClientBinding(ProducerBinding, RpcMixin):
    pass


class RpcServerBinding(ConsumerBinding, RpcMixin):
    def __init__(self, queue, exchange):
        super().__init__(queue, exchange)
