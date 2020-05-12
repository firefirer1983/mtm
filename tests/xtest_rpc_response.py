import pika
import uuid
import sys
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))


connection = pika.BlockingConnection(
    parameters=pika.URLParameters("amqp://guest:guest@localhost:5672/%2F")
)
channel = connection.channel()

channel.queue_declare(queue="rpc_set_id")


def on_request(ch, method, props, body):
    n = int(body)

    response = "[%r]rpc set id ok!" % n

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=str(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="rpc_set_id", on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
