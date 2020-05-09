import logging
from pika import BlockingConnection
from pika.connection import URLParameters
import json
from mtm.model.models import User
from mtm.model.database import scoped_session


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

log = logging.getLogger(__file__)


def main():
    connection = BlockingConnection(
        parameters=URLParameters("amqp://guest:guest@localhost:5672/%2F")
    )
    ch = connection.channel()
    ch.exchange_declare(exchange="worker.mm", exchange_type="topic")
    with scoped_session(auto_commit=False) as ssn:
        users = ssn.query(User).filter_by(disable=False)
        with open("scripts/vd_list.txt", "r") as f:
            for ind, url in enumerate(f.readlines()):
                url = url.strip()
                if url:
                    log.info("%s:%s" % (users[ind % 5].username, url))
                    ch.basic_publish(
                        exchange="worker.mm",
                        routing_key="request.download",
                        body=json.dumps(
                            {"url": url, "username": users[ind % 5].username},
                            ensure_ascii=True,
                        ),
                    )


if __name__ == "__main__":
    main()
