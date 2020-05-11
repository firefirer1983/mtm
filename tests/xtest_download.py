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
    ch.basic_publish(
        exchange="worker.mm",
        routing_key="request.download",
        properties=props,
        body=json.dumps(
            {
                "url": "https://www.youtube.com/watch?v=PJ1QwhNL72A",
                "username": "naeidzwwwwzlzzzz",
            },
        ),
    )


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
