import logging
from .base.poll import Poll

from .mq.binding import ConsumerBinding
from .mq.exchange import TopicExchange
from .mq.queue import RabbitQueue

log = logging.getLogger(__file__)

status_binding = ConsumerBinding(
    RabbitQueue("crawler_activity_status_q"), TopicExchange("worker.mm"),
)


@status_binding.listen_on(binding_key="crawler.*.status")
def crawl_status_handler(channel, basic_deliver, properties, body):
    log.info("status:")
    log.info(channel)
    log.info(basic_deliver)
    log.info(properties)
    log.info(body)
    channel.basic_ack(basic_deliver.delivery_tag)


class Transporter(Poll):
    def __init__(self):
        super().__init__(status_binding)
        self.set_poll_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
