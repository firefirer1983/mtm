import pika
import uuid
import sys
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))


class RpcClient:
    def __init__(self):
        self._rsp = None
        self._corr_id = None
        self.connection = pika.BlockingConnection(
            parameters=pika.URLParameters(
                "amqp://guest:guest@localhost:5672/%2F"
            )
        )

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

    def on_response(self, ch, method, props, body):
        if self._corr_id == props.correlation_id:
            self._rsp = body

    def call(self, n):
        self._rsp = None
        self._corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange="",
            routing_key="rcp_get_id",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue, correlation_id=self._corr_id,
            ),
            body=str(n),
        )
        while self._rsp is None:
            self.connection.process_data_events()
        return str(self._rsp)


rpc_client = RpcClient()

print(" [x] Requesting rpc get id")
response = rpc_client.call(30)
print(" [.] Got %r" % response)
