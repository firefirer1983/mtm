import json
import logging
from .base.poll import Poll

from .mq.binding import ConsumerBinding, Binding
from .mq.exchange import TopicExchange
from .mq.queue import RabbitQueue

log = logging.getLogger(__file__)

action_binding = ConsumerBinding(
    RabbitQueue("transporter_action_q"), TopicExchange("worker.mm")
)

status_binding = Binding(
    RabbitQueue("transporting_activity_status_q"), TopicExchange("worker.mm")
)


@action_binding.listen_on(binding_key="transporter.search")
def transporter_search_handler(channel, basic_deliver, properties, body):
    log.info(channel, basic_deliver, properties, body)
    url = json.loads(body)["url"]
    channel.basic_ack(basic_deliver.delivery_tag)
    channel.publish_message(
        exchange="worker.mm",
        routing_key="transporting.search.status",
        message={"search": "not found", "url": url},
    )


@action_binding.listen_on(binding_key="transporter.upload")
def transporter_upload_handler(channel, basic_deliver, properties, body):
    log.info(channel, basic_deliver, properties, body)
    url = json.loads(body)["url"]
    channel.basic_ack(basic_deliver.delivery_tag)
    channel.publish_message(
        exchange="worker.mm",
        routing_key="transporting.upload.status",
        message={"upload": "finished", "url": url},
    )


class Transporter(Poll):
    def __init__(self):
        super().__init__(status_binding, action_binding)
        self.set_poll_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
