import logging
from pika import BlockingConnection, BasicProperties
from pika.connection import URLParameters
import json


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
    ch.queue_declare(queue="splitter_action_request_q")
    ch.queue_bind(
        queue="splitter_action_request_q",
        exchange="worker.mm",
        routing_key="splitter.*.request",
    )
    ch.basic_publish(
        exchange="worker.mm",
        routing_key="splitter.split.request",
        properties=props,
        body=json.dumps(
            {
                "cache_dir": "/home/xy/repo/python/mtm/cache/youtube/好葉怎樣練習冥想完整教學 動畫講解-NLJcwbpkiJ0",
                "action.type": "split",
                "partial_duration": 2 * 60,
            }
        ),
    )


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
