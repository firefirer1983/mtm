import abc
from .queue import RabbitQueue
from .exchange import TopicExchange, default_exchange, DefaultExchange
import logging

log = logging.getLogger(__name__)


class Binding(abc.ABC):
    def __init__(self, queue, exchange):
        self._queue = queue
        self._exchange = exchange
        self._channel = None

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

    @property
    def is_producer(self):
        return True


class ConsumerMixin:
    @property
    def is_consumer(self):
        return True

    @property
    def is_producer(self):
        return False


class RpcMixin:
    @property
    def is_rpc(self):
        return True


class ConsumerBinding(Binding, ConsumerMixin):
    def __init__(
        self,
        q_name,
        ex_name,
        binding_key=None,
        exclusive=False,
        auto_ack=False,
    ):
        super().__init__(
            RabbitQueue(
                q_name,
                binding_key=binding_key,
                exclusive=exclusive,
                auto_ack=auto_ack,
            ),
            default_exchange
            if ex_name == "default"
            else TopicExchange(ex_name),
        )


class ProducerBinding(Binding):
    def __init__(self, q_name, ex_name, exclusive=False, auto_ack=False):
        super().__init__(
            RabbitQueue(q_name, exclusive=exclusive, auto_ack=auto_ack),
            default_exchange
            if ex_name == "default"
            else TopicExchange(ex_name),
        )


# RPC Client 的response consumer需要 auto ack
class RpcClientBinding(ProducerBinding, RpcMixin):
    def __init__(self, q_name, ex_name):
        super().__init__(q_name, ex_name, auto_ack=True)


# RPC Server 的 request queue需要exclusive
class RpcServerBinding(ConsumerBinding, RpcMixin):
    def __init__(self, q_name, ex_name):
        super().__init__(q_name, ex_name, exclusive=True)
