import abc
import json
import logging
from pika import BasicProperties

from .channel import Channel
from ..base.poll import Poll
from ..base.service import MessageConsumer, MessageProducer
from .binding import Binding


log = logging.getLogger(__file__)

APP_ID = "mtm"


class RabbitConsumer(MessageConsumer):
    def __init__(self, binding_key, queue, exchange):
        self._binding = Binding(queue, exchange)
        self._binding.set_binding_key(binding_key)
        self._binding.register_on_message_callback(self.on_message)

    def consumer_tag(self):
        return self._binding.queue.consumer_tag

    def __str__(self):
        return "<RabbitCustomer> with binding:%s" % self._binding

    @abc.abstractmethod
    def on_message(self, *args, body):
        pass


class RabbitListener:
    def __init__(self, binding_key, queue, exchange):
        self._binding = Binding(queue, exchange)
        self._binding.set_binding_key(binding_key)

    def consumer_tag(self):
        return self._binding.queue.consumer_tag

    def __call__(self, cb):
        self._binding.register_on_message_callback(cb)


class RabbitProducer(MessageProducer):
    def __init__(self, queue, exchange):
        self._binding = Binding(queue, exchange)
        self._channel = None

    def publish_json(self, routing_key, message):
        properties = BasicProperties(
            app_id=APP_ID, content_type="application/json", headers=None
        )
        body = json.dumps(message, ensure_ascii=False)
        self.publish_message(routing_key, message=body, properties=properties)

    def publish_message(self, routing_key, message, properties=None):
        assert self._binding.channel, "Please attach channel before publishing"
        self._binding.channel.publish_message(
            self._binding.exchange,
            routing_key,
            body=message,
            properties=properties,
        )

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
