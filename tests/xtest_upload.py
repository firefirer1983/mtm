import logging
from pika import BlockingConnection
from pika.connection import URLParameters
import json


def main():
    connection = BlockingConnection(
        parameters=URLParameters("amqp://guest:guest@localhost:5672/%2F")
    )
    ch = connection.channel()
    ch.basic_publish(
        exchange="worker.mm",
        routing_key="request.upload",
        body=json.dumps(
            {
                "url": "https://www.youtube.com/watch?v=PJ1QwhNL72A",
                "username": "xy",
            },
            ensure_ascii=True,
        ),
    )


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
