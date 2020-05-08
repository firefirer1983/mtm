import json
import logging
from .crawler import Crawler
from .rabbit.binding import Binding, ConsumerBinding
from .rabbit.exchange import TopicExchange
from .rabbit.queue import RabbitQueue
from .base.poll import Poll


log = logging.getLogger(__file__)

activity_binding = ConsumerBinding(
    RabbitQueue("crawler_activity_q"), TopicExchange("worker.mm"),
)

status_binding = Binding(
    RabbitQueue("crawler_activity_status_q"), TopicExchange("worker.mm"),
)


@activity_binding.listen_on("crawler.start")
def crawl_start_handler(channel, basic_deliver, properties, body):
    log.info("check status request:")
    log.info(channel)
    log.info(basic_deliver)
    log.info(properties)
    log.info(body)
    url = json.loads(body)["url"]
    cwl = Crawler()
    res = cwl.validate_url(url)
    print("validate: %r" % res)
    channel.basic_ack(basic_deliver.delivery_tag)
    channel.basic_publish(
        exchange="worker.mm",
        routing_key="crawler.validate.status",
        body=json.dumps(res, ensure_ascii=True),
    )

    cwl.download(url)
    channel.basic_publish(
        "worker.mm",
        routing_key="crawler.download.status",
        body=json.dumps({"result": "finished"}, ensure_ascii=True),
    )


class CrawlWorker(Poll):
    def __init__(self):
        super().__init__(activity_binding, status_binding)
        self.set_poll_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
