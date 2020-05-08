import json
import pika
import functools
import logging

APP_ID = "mtm"

log = logging.getLogger(__name__)


class Channel:
    def __init__(self, url, *bindings):
        self._url = url
        self._connection = pika.SelectConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed,
        )
        self._rabbit_channel = None
        self._bindings = bindings
        self._stopping = False
        self._consumer_queue_count = 0
        self._poll_fn = None
        self._poll_interval = None
        self._should_reconnect = False

        self._deliveries = None
        self._acked = None
        self._nacked = None
        self._message_number = None

    @property
    def rabbit_channel(self):
        return self._rabbit_channel

    @property
    def consumer_queue_count(self):
        return self._consumer_queue_count

    def activate_consumer_queue(self):
        self._consumer_queue_count += 1

    def deactivate_consumer_queue(self):
        self._consumer_queue_count -= 1

    def close_connection(self):
        if self._connection.is_closing or self._connection.is_closed:
            log.info("Connection is closing or already closed")
        else:
            log.info("Closing connection")
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        log.info("Connection opened")
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        log.error("Connection open failed: %s", err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        self._rabbit_channel = None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            log.warning("Connection closed, reconnect necessary: %s", reason)
            self.reconnect()

    def reconnect(self):
        self._should_reconnect = True
        self.stop()

    def open_channel(self):
        log.info("Creating a new channel")
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        log.info("Channel opened")
        self._rabbit_channel = channel
        self._rabbit_channel.activate_consumer_queue = (
            self.activate_consumer_queue
        )
        self._rabbit_channel.deactivate_consumer_queue = (
            self.deactivate_consumer_queue
        )
        self.add_on_channel_close_callback()
        self.setup_exchanges()

    def add_on_channel_close_callback(self):
        log.info("Adding channel close callback")
        self._rabbit_channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        log.warning("Channel %i was closed: %s", channel, reason)
        self.close_connection()

    def enable_delivery_confirmations(self):
        log.info("Issuing Confirm.Select RPC command")
        self._rabbit_channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split(".")[1].lower()
        log.info(
            "Received %s for delivery tag: %i",
            confirmation_type,
            method_frame.method.delivery_tag,
        )
        if confirmation_type == "ack":
            self._acked += 1
        elif confirmation_type == "nack":
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        log.info(
            "Published %i messages, %i have yet to be confirmed, "
            "%i were acked and %i were nacked",
            self._message_number,
            len(self._deliveries),
            self._acked,
            self._nacked,
        )

    def publish_message(self, exchange, routing_key, hdrs, message):

        if self._rabbit_channel is None or not self._rabbit_channel.is_open:
            return

        properties = pika.BasicProperties(
            app_id=APP_ID, content_type="application/json", headers=hdrs,
        )

        self._rabbit_channel.basic_publish(
            exchange,
            routing_key,
            json.dumps(message, ensure_ascii=False),
            properties,
        )
        self._message_number += 1
        self._deliveries.append(self._message_number)
        log.info("Published message # %i", self._message_number)

    def setup_exchanges(self):
        log.error("bindings: %r", self._bindings)
        for binding in self._bindings:
            exchange = binding.exchange
            exchange.attach_channel(self._rabbit_channel)
            cb = functools.partial(exchange.setup_queues, binding)
            self._rabbit_channel.exchange_declare(
                exchange=str(exchange),
                exchange_type=binding.exchange.exchange_type,
                callback=cb,
            )
        self.enable_delivery_confirmations()

    def close_channel(self):
        log.info("Closing the channel")
        self._rabbit_channel.close()

    def _poll_wrapper(self):
        if self._poll_fn:
            self._poll_fn()
            self._connection.ioloop.call_later(
                self._poll_interval, self._poll_wrapper
            )

    def stop(self):
        if not self._stopping:
            self._stopping = True
            log.info("Stopping")
            if self.consumer_queue_count:
                for binding in self._bindings:
                    self.stop_consuming(binding.queue)
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            log.info("Stopped")

    def stop_consuming(self, queue):
        if self._rabbit_channel:
            log.info("Sending a Basic.Cancel RPC command to RabbitMQ")
            cb = functools.partial(
                queue.on_cancelok, userdata=queue.consumer_tag
            )
            self._rabbit_channel.basic_cancel(queue.consumer_tag, cb)

    def install_poll(self, poll, interval):
        self._poll_interval = interval
        self._poll_fn = poll

    def run(self):
        while not self._stopping:
            if self._poll_fn:
                self._connection.ioloop.call_later(
                    self._poll_interval, self._poll_wrapper
                )

            self._deliveries = []
            self._acked = 0
            self._nacked = 0
            self._message_number = 0

            try:
                self._connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if (
                    self._connection is not None
                    and not self._connection.is_closed
                ):
                    # Finish closing
                    self._connection.ioloop.start()

        log.info("Stopped")
