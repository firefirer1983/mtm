#!/usr/bin/env python
import pika
import sys
from pika import BlockingConnection, URLParameters


connection = BlockingConnection(
    parameters=URLParameters("amqp://guest:guest@localhost:5672/%2F")
)
channel = connection.channel()

channel.exchange_declare(exchange="topic_logs", exchange_type="topic")

result = channel.queue_declare("", exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange="topic_logs", queue=queue_name, routing_key="*.info"
)

print(" [*] Waiting for logs. To exit press CTRL+C")


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True
)

channel.start_consuming()
