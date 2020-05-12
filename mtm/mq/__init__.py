import abc
import pika
import json
import logging
import uuid

from pika import BasicProperties

from .connection import BlockingConnection
from .rabbit_ctx import rabbit_context

from .channel import Channel
from ..base.poll import Poll
from ..base.service import (
    MessageConsumer,
    MessageProducer,
    RpcClient,
    RpcServer,
)
from .binding import (
    ConsumerBinding,
    ProducerBinding,
    RpcClientBinding,
    RpcServerBinding,
)


log = logging.getLogger(__file__)

APP_ID = "mtm"


class RabbitConsumer(MessageConsumer):
    def __init__(self, binding_key, queue, exchange):
        self._binding = ConsumerBinding(queue, exchange, binding_key)
        self._binding.queue.register_on_message_callback(self.on_message)
        rabbit_context.add_consumer(self)

    @property
    def consumer_id(self):
        return self._binding.queue.consumer_tag

    def __str__(self):
        return "<RabbitCustomer> with binding:%s" % self._binding

    @abc.abstractmethod
    def on_message(self, *args, body):
        pass

    @property
    def binding(self):
        return self._binding


class RabbitListener:
    def __init__(self, binding_key, queue, exchange):
        self._binding = ConsumerBinding(queue, exchange, binding_key)
        rabbit_context.add_consumer(self)

    @property
    def consumer_id(self):
        return self._binding.queue.consumer_tag

    def __call__(self, cb):
        self._binding.queue.register_on_message_callback(cb)

    @property
    def binding(self):
        return self._binding


class RabbitRpcServer(RpcServer):
    def __init__(self, queue):
        self._binding = RpcServerBinding(queue, "default")
        self._binding.queue.register_on_request_callback(self.on_request)
        rabbit_context.add_consumer(self)

    @property
    def consumer_id(self):
        return self._binding.queue.consumer_tag

    def __str__(self):
        return "<RabbitRpcServer> with binding:%s" % self._binding

    @property
    def binding(self):
        return self._binding

    def on_request(self, body):
        pass


class RabbitRpcListener:
    def __init__(self, queue):
        self._binding = RpcServerBinding(queue, "default")
        rabbit_context.add_consumer(self)

    def __call__(self, cb):
        self._binding.queue.register_on_request_callback(cb)

    @property
    def binding(self):
        return self._binding


class RabbitProducer(MessageProducer):
    def __init__(self, queue, exchange):
        self._binding = ProducerBinding(queue, exchange)
        rabbit_context.add_producer(self)

    def publish_json(self, routing_key, message):
        properties = BasicProperties(
            app_id=APP_ID, content_type="application/json", headers=None
        )
        body = json.dumps(message, ensure_ascii=False)
        self.publish_message(routing_key, properties=properties, message=body)

    def publish_message(self, routing_key, properties, message):
        return self._binding.channel.publish_message(
            self._binding.exchange,
            routing_key=routing_key,
            properties=properties,
            body=message,
        )

    @property
    def producer_id(self):
        return "%s:%s" % (self._binding.exchange, self._binding.queue)

    @property
    def binding(self):
        return self._binding

    def __str__(self):
        return "<RabbitProducer> with binding:%s" % self._binding


class RabbitRpcClient(RpcClient):
    def connect(self, url):
        self._connection = BlockingConnection(url=url)
        self._rabbit_channel = self._connection.channel
        return self

    def __init__(self, routing_key):
        self._connection = None
        self._routing_key = routing_key
        self._rabbit_channel = None
        self._callback_queue = None
        self._corr_id = None
        self._rsp = None

    def _on_response(self, ch, method, props, body):
        if self._corr_id == props.correlation_id:
            self._rsp = body

    def call(self, msg):
        assert self._connection, "Connect Before Rpc Call!"
        result = self._rabbit_channel.queue_declare(queue="", exclusive=True)
        self._callback_queue = result.method.queue
        self._corr_id = None
        self._rabbit_channel.basic_consume(
            queue=self._callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )
        self._rsp = None
        self._corr_id = str(uuid.uuid4())
        self._rabbit_channel.basic_publish(
            exchange="",
            routing_key=str(self._routing_key),
            properties=pika.BasicProperties(
                reply_to=self._callback_queue, correlation_id=self._corr_id,
            ),
            body=str(msg),
        )
        while self._rsp is None:
            self._connection.poll_event()
        self._rabbit_channel.queue_delete(self._callback_queue)
        return self._rsp


class RabbitPoll(Poll):
    def __init__(self, url):
        self._interval = 200
        self._channel = Channel(url)

    def get_interval(self):
        return self._interval

    def set_interval(self, interval):
        self._interval = interval

    def run(self):
        self._channel.install_poll(self.poll, self._interval)
        self._channel.run()

    @abc.abstractmethod
    def poll(self):
        pass
