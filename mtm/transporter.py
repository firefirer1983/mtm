import json
import logging
from .base.poll import Poll

from .mq.binding import Consumer, Producer
from .mq.channel import ch

log = logging.getLogger(__file__)

action_search_consumer = Consumer("transporter_action_q", "worker.mm")
action_upload_consumer = Consumer("transporter_action_q", "worker.mm")
activity_status_producer = Producer(
    "transporting_activity_status_q", "worker.mm"
)


@action_search_consumer.listen_on(binding_key="transporter.search")
def transporter_search_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    url = json.loads(body)["url"]
    channel.basic_ack(basic_deliver.delivery_tag)
    channel.publish_message(
        exchange="worker.mm",
        routing_key="transporting.search.status",
        message={"search": "not found", "url": url},
    )


@action_upload_consumer.listen_on(binding_key="transporter.upload")
def transporter_upload_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    url = json.loads(body)["url"]
    channel.basic_ack(basic_deliver.delivery_tag)
    channel.publish_message(
        exchange="worker.mm",
        routing_key="transporting.upload.status",
        message={"upload": "finished", "url": url},
    )


class Transporter(Poll):
    def __init__(self):
        super().__init__(ch, None)
        self.set_poll_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
