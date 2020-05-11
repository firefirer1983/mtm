import abc
import json
import logging
import time
import uuid

from pika import BasicProperties

from .rabbit_ctx import rabbit_context

from .channel import Channel
from ...core.service.poll import Poll
from cpg.core.mq import MessageConsumer, MessageProducer
from .binding import Binding


log = logging.getLogger(__file__)

APP_ID = "mtm"


class RabbitConsumer(MessageConsumer):
    def __init__(self, binding_key, queue, exchange):
        self._binding = Binding(queue, exchange)
        self._binding.set_binding_key(binding_key)
        self._binding.register_on_message_callback(self.on_message)
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
        self._binding = Binding(queue, exchange)
        self._binding.set_binding_key(binding_key)
        rabbit_context.add_consumer(self)

    @property
    def consumer_id(self):
        return self._binding.queue.consumer_tag

    def __call__(self, cb):
        self._binding.register_on_message_callback(cb)

    @property
    def binding(self):
        return self._binding


class RpcListener:
    def __init__(self, queue):
        self._binding = Binding(queue, None)
        self._binding.set_binding_key(binding_key=str(self._binding.queue))
        rabbit_context.add_consumer(self)

    def __call__(self, cb):
        self._binding.queue.register_on_rpc_request_callback(cb)

    @property
    def binding(self):
        return self._binding


class RpcClient:
    def __init__(self, routing_key, queue):
        self._routing_key = routing_key
        self._binding = Binding(queue, None)
        self._rsp = None
        self._corr_id = None

    def call(self, msg):
        self._rsp = None
        self._corr_id = str(uuid.uuid4())
        properties = BasicProperties(
            reply_to=str(self._binding.queue),
            content_type="application/json",
            correlation_id=self._corr_id,
        )
        self._binding.channel.publish_message(
            exchange="",
            routing_key=self._routing_key,
            properties=properties,
            body=msg,
        )
        while self._rsp is None:
            time.sleep(0.1)
        return self._rsp

    @property
    def producer_id(self):
        return "%s:%s" % (self._binding.queue, self._routing_key)

    def __call__(self):
        self._binding.register_on_response_callback(self._on_response)

    def _on_response(self, body):
        self._rsp = body


class RabbitProducer(MessageProducer):
    def __init__(self, queue, exchange):
        self._binding = Binding(queue, exchange)
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


class RabbitPoll(Poll):
    def __init__(self, url):
        self._interval = 500
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
