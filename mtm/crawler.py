import json
import logging
from .components.downloader import Downloader
from .mq.binding import Producer, Consumer
from .base.poll import Poll
from .model.models import Transmission, TxStatus
from .model.database import scoped_session
from .mq.channel import ch


log = logging.getLogger(__file__)


action_validate_consumer = Consumer("crawler_action_q", "worker.mm")
action_download_consumer = Consumer("crawler_action_q", "worker.mm")
activity_status_producer = Producer("crawling_activity_status_q", "worker.mm")


@action_validate_consumer.listen_on("crawler.validate")
def crawler_validate_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    url = json.loads(body)["url"]
    channel.basic_ack(basic_deliver.delivery_tag)

    valid = False
    with scoped_session() as s:
        tx = Transmission.get_transmission(ssn=s, url=url)
        dwl = Downloader()
        res = dwl.validate_url(tx.url)
        if res:
            tx.status = TxStatus.valid
            valid = True
        else:
            tx.status = TxStatus.invalid

    channel.publish_message(
        exchange="worker.mm",
        routing_key="crawling.validate.status",
        message={"valid": valid, "url": url},
    )


@action_download_consumer.listen_on("crawler.download")
def crawler_download_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    url = json.loads(body)["url"]
    channel.basic_ack(basic_deliver.delivery_tag)
    with scoped_session() as ssn:
        tx = Transmission.get_transmission(ssn, url)
        try:
            dwl = Downloader()
            tx.status = TxStatus.downloading
            dwl.download(tx.url)
        except Exception as e:
            tx.status = TxStatus.download_fail
            downloaded = False
            message = "Download Fail"
            log.exception(e)
        else:
            tx.status = TxStatus.downloaded
            downloaded = True
            message = "Download Finished"

    channel.publish_message(
        exchange="worker.mm",
        routing_key="crawling.download.status",
        message={"download": downloaded, "message": message, "url": url},
    )


class Crawler(Poll):
    def __init__(self):
        super().__init__(ch, None)
        self.set_poll_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
