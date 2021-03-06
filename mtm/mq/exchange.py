import functools
import logging

log = logging.getLogger(__name__)


class Exchange:
    def __init__(self, exchange_name, exchange_type):
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type
        self._channel = None

    @property
    def exchange_type(self):
        return self._exchange_type

    @property
    def exchange_name(self):
        return self._exchange_name

    def __str__(self):
        return str(self.exchange_name)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return str(self) == str(other)

    def attach_channel(self, channel):
        self._channel = channel

    def setup_queue(self, binding, _unused_frame):
        log.info(_unused_frame)
        log.info(binding)
        queue = binding.queue
        queue.attach_channel(self._channel)
        log.info(
            "binding:%s need_binding:%u is_consumer:%u is_producer:%u is_rpc:%u"
            % (
                binding,
                binding.need_binding,
                binding.is_consumer,
                binding.is_producer,
                binding.is_rpc,
            )
        )

        if binding.need_binding:
            cb = functools.partial(
                queue.setup_binding, userdata=binding
            )
        elif binding.is_rpc and binding.is_consumer:
            cb = queue.setup_qos
        else:
            cb = lambda x: x
        self._channel.queue_declare(
            queue=str(queue), callback=cb, exclusive=queue.exclusive
        )

    @property
    def is_default(self):
        return self._exchange_type == "default"


class TopicExchange(Exchange):
    def __init__(self, exchange_name):
        super().__init__(exchange_name, "topic")


class DefaultExchange(Exchange):
    def __init__(self):
        super().__init__("", "default")


default_exchange = DefaultExchange()
