import json
import logging
from .mq import RabbitListener, RabbitProducer, RabbitPoll

log = logging.getLogger(__file__)


search_status_publisher = RabbitProducer(
    "transporting_search_status_q", "worker.mm"
)
upload_status_publisher = RabbitProducer(
    "transporting_upload_status_q", "worker.mm"
)


@RabbitListener(
    binding_key="transporter.search",
    queue="transporter_search_q",
    exchange="worker.mm",
)
def transporter_search_handler(msg):
    log.info("%r" % msg)
    url = json.loads(msg)["url"]
    search_status_publisher.publish_json(
        routing_key="transporting.search.status",
        message={"search": "not found", "url": url},
    )


@RabbitListener(
    binding_key="transporter.upload",
    queue="transporter_upload_q",
    exchange="worker.mm",
)
def transporter_upload_handler(msg):
    log.info("%r" % msg)
    url = json.loads(msg)["url"]
    upload_status_publisher.publish_json(
        routing_key="transporting.upload.status",
        message={"upload": "finished", "url": url},
    )


class Transporter(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self.set_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
