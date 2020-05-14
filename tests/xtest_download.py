import logging
from pika import BlockingConnection, BasicProperties
from pika.connection import URLParameters
import json


def print_msg(ch, method, props, body):
    print(body)
    ch.basic_ack(method.delivery_tag)


def main():
    connection = BlockingConnection(
        parameters=URLParameters("amqp://guest:guest@localhost:5672/%2F")
    )
    props = BasicProperties(
        content_type="application/json",
        content_encoding="utf8",
        delivery_mode=2,
    )
    ch = connection.channel()
    ch.exchange_declare(exchange="worker.mm", exchange_type="topic")
    ch.queue_declare(queue="crawler_action_request_q")
    ch.queue_bind(
        queue="crawler_action_request_q",
        exchange="worker.mm",
        routing_key="crawler.*.request",
    )
    ch.basic_publish(
        exchange="worker.mm",
        routing_key="crawler.download.request",
        properties=props,
        body=json.dumps(
            {
                "url": "https://www.youtube.com/watch?v=NLJcwbpkiJ0",
                "username": "naeidzwwwwzlzzzz",
            }
        ),
    )
    print("published download request=======================>")
    
    ch.queue_declare(queue="worker_action_result_q")
    ch.queue_bind(
        "worker_action_result_q", "worker.mm", routing_key="*.*.result"
    )
    ch.basic_consume(
        "worker_action_result_q",
        auto_ack=True,
        on_message_callback=print_msg,
        consumer_tag="xtesting",
    )
    ch.start_consuming()


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
