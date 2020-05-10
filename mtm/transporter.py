import json
import logging
from .base.poll import Poll

from .mq.binding import Consumer, Producer
from .mq.channel import ch

log = logging.getLogger(__file__)


search_status_publisher = Producer("transporting_search_status_q", "worker.mm")
upload_status_publisher = Producer("transporting_upload_status_q", "worker.mm")


@Consumer(
    binding_key="transporter.search",
    queue="transporter_search_q",
    exchange="worker.mm",
)
def transporter_search_handler(*args, body):
    log.info("%r" % body)
    url = json.loads(body)["url"]
    search_status_publisher.publish_json(
        routing_key="transporting.search.status",
        message={"search": "not found", "url": url},
    )


@Consumer(
    binding_key="transporter.upload",
    queue="transporter_upload_q",
    exchange="worker.mm",
)
def transporter_upload_handler(*args, body):
    log.info("%r" % body)
    url = json.loads(body)["url"]
    upload_status_publisher.publish_json(
        routing_key="transporting.upload.status",
        message={"upload": "finished", "url": url},
    )


class Transporter(Poll):
    def __init__(self):
        super().__init__(ch, None)
        self.set_poll_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
