#!/usr/bin/env python
import pika
import sys

from pika import BlockingConnection, URLParameters


connection = BlockingConnection(
    parameters=URLParameters("amqp://guest:guest@localhost:5672/%2F")
)
channel = connection.channel()

channel.exchange_declare(exchange="topic_logs", exchange_type="topic")

routing_key = "anonymous.info"
message = " ".join(sys.argv[2:]) or "Hello World!"
channel.basic_publish(
    exchange="topic_logs", routing_key=routing_key, body=message
)
print(" [x] Sent %r:%r" % (routing_key, message))
connection.close()
