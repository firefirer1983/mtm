import os
import logging
from pika import BlockingConnection, BasicProperties
from pika.connection import URLParameters
import json

log = logging.getLogger(__file__)
CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
YOUTUBE_CACHE_REPO = os.path.join(CACHE_REPO, "youtube")


def print_msg(ch, method, props, body):
    log.info("%s: %r" % (method.routing_key, body))
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
    url_list = [
        "https://www.youtube.com/watch?v=PJ1QwhNL72A",
        # "https://www.youtube.com/watch?v=b5K192_hilA",
        # "https://www.youtube.com/watch?v=L0skErRNc5Y",
        # "https://www.youtube.com/watch?v=G8GWtGZuHSk",
        # "https://www.youtube.com/watch?v=Vn4wxZlaFYc",
        # "https://www.youtube.com/watch?v=ObO6XEQSWak",
        # "https://www.youtube.com/watch?v=fPz2tZibAAQ",
        # "https://www.youtube.com/watch?v=v0ADJy2Menk",
    ]
    for url in url_list:
        ch.basic_publish(
            exchange="worker.mm",
            routing_key="crawler.download.request",
            properties=props,
            body=json.dumps(
                {
                    "url": url,
                    "username": "naeidzwwwwzlzzzz",
                    "cache_path": YOUTUBE_CACHE_REPO,
                }
            ),
        )

    ch.queue_declare(queue="worker_action_result_q")
    ch.queue_bind(
        "worker_action_result_q", "worker.mm", routing_key="*.*.result"
    )
    ch.basic_consume(
        "worker_action_result_q",
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
