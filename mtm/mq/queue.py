import logging
from pika import BasicProperties

log = logging.getLogger(__name__)


def wrap_cb_with_ack(cb):
    def _f(channel, basic_deliver, properties, body):

        try:
            ret = cb(body)
        except Exception as e:
            log.exception(e)
            raise
        else:
            channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)
        return ret

    return _f


def wrap_rpc_request_with_ack(cb):
    def _f(channel, method, properties, body):
        try:
            ret = cb(body)

            channel.publish_message(
                exchange="",
                routing_key=properties.reply_to,
                properties=BasicProperties(
                    correlation_id=properties.correlation_id
                ),
                body=str(ret),
            )
        except Exception as e:
            log.exception(e)
            raise
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    return _f


def wrap_rpc_response(cb, corr_id):
    def _f(channel, method, properties, body):
        if corr_id == properties.correlation_id:
            cb(body)

    return _f


class RabbitQueue:
    def __init__(self, queue_name, qos=1):
        self._name = queue_name
        self._qos = qos
        self._channel = None
        self._binding_key = None
        self.was_consuming = True
        self._consuming = False
        self._consumer_tag = None
        self._on_message = None
        self._exclusive = False
        self._auto_ack = False

    def register_on_message_callback(self, cb):
        self._on_message = wrap_cb_with_ack(cb)

    def register_on_request_callback(self, cb):
        self._on_message = wrap_rpc_request_with_ack(cb)

    def register_on_response_callback(self, corr_id, cb):
        self._on_message = wrap_rpc_response(cb, corr_id)

    def attach_channel(self, channel):
        self._channel = channel

    def setup_binding(self, _unused_frame, userdata):
        self._channel.queue_bind(
            self._name,
            userdata,
            routing_key=self.binding_key,
            callback=self.setup_qos,
        )

    def setup_qos(self, _unused_frame):
        if not self._name:
            self._name = _unused_frame.method.queue
        self._channel.basic_qos(
            prefetch_count=self._qos, callback=self.start_consuming
        )

    @property
    def consumer_tag(self):
        return self._consumer_tag

    def start_consuming(self, _unused_frame):
        log.info("Issuing consumer related RPC commands")
        self.add_on_cancel_callback()
        print("%s: on_message:%r" % (self._name, self._on_message))
        self._consumer_tag = self._channel.basic_consume(
            self._name, self._on_message, auto_ack=self.is_auto_ack
        )
        self.was_consuming = True
        self._consuming = True

        self._channel.activate_consumer_queue()
    
    def start_consuming_rpc(self):
        log.info("Issuing consumer related RPC commands")
        print("%s: on_message:%r" % (self._name, self._on_message))
        self._consumer_tag = self._channel.basic_consume(
            self._name, self._on_message, auto_ack=self.is_auto_ack
        )
        self.was_consuming = True
        self._consuming = True
    
        self._channel.activate_consumer_queue()

    def add_on_cancel_callback(self):
        log.info("Adding consumer cancellation callback")
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_cancelok(self, _unused_frame, userdata):

        self._consuming = False
        log.info(
            "RabbitMQ acknowledged the cancellation of the consumer: %s",
            userdata,
        )
        self._channel.deactivate_consumer_queue()
        if self._channel.consumer_queue_count == 0:
            self._channel.close_channel()

    def on_consumer_cancelled(self, method_frame):
        log.info(
            "Queue: %s Consumer was cancelled remotely, shutting down: %r",
            self._name,
            method_frame,
        )
        self._channel.deactivate_consumer_queue()
        if self._channel.consumer_queue_count <= 0:
            self._channel.close_channel()

    def set_exclusive(self):
        self._exclusive = True

    def set_auto_ack(self):
        self._auto_ack = True

    @property
    def is_exclusive(self):
        return self._exclusive

    @property
    def is_auto_ack(self):
        return self._auto_ack

    def set_queue_name(self, name):
        log.info("set queue name:%s" % name)
        self._name = str(name)

    def __str__(self):
        return str(self._name)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return str(self) == str(other)

    @property
    def binding_key(self):
        return self._binding_key

    @binding_key.setter
    def binding_key(self, val):
        self._binding_key = val
