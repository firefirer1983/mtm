import json
import logging
from .components.downloader import Downloader
from .mq import RabbitListener, RabbitProducer, RabbitPoll
from .model.models import Transmission, TxStatus
from .model.database import scoped_session


log = logging.getLogger(__file__)


status_publisher = RabbitProducer(
    queue="crawling_activity_status_q", exchange="worker.mm"
)


@RabbitListener(
    binding_key="crawler.validate",
    queue="crawler_action_validate_q",
    exchange="worker.mm",
)
def crawler_validate_handler(msg):
    log.info("%r" % msg)
    url = json.loads(msg)["url"]

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

    status_publisher.publish_json(
        routing_key="crawling.validate.status",
        message={"valid": valid, "url": url},
    )


@RabbitListener(
    binding_key="crawler.download",
    queue="crawler_action_download_q",
    exchange="worker.mm",
)
def crawler_download_handler(msg):
    log.info("%r" % msg)
    url = json.loads(msg)["url"]

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

    status_publisher.publish_json(
        routing_key="crawling.download.status",
        message={"download": downloaded, "message": message, "url": url},
    )


class Crawler(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self.set_interval(10)

    def poll(self):
        log.debug("Transaction status polling alive!")
