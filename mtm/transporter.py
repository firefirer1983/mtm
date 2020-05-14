import json
import logging
from .mq import RabbitListener, RabbitProducer, RabbitPoll

log = logging.getLogger(__file__)


result_publisher = RabbitProducer("worker_action_result_q", "worker.mm")


@RabbitListener(
    binding_key="transporter.*",
    queue="worker_action_request_q",
    exchange="worker.mm",
)
def transporter_action_handler(msg):
    log.info("%r" % msg)
    url = json.loads(msg)["url"]
    if msg["action.name"] == "search":

        result_publisher.publish_json(
            routing_key="transporter.search.result",
            message={"search": True, "url": url, "message": "Search Found!"},
        )
    elif msg["action.name"] == "upload":
        url = json.loads(msg)["url"]
        result_publisher.publish_json(
            routing_key="transporter.upload.result",
            message={"upload": True, "url": url, "message": "Upload Finished"},
        )
    else:
        log.error("Unknown msg:%r" % msg)


class Transporter(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self.set_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
