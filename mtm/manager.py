import json
import logging

from .mq import RabbitListener, RabbitProducer, RabbitPoll
from .model.models import Transmission, User
from .model.database import scoped_session

log = logging.getLogger(__file__)

crawler_action_publisher = RabbitProducer("crawler_action_q", "worker.mm")
transporter_action_publisher = RabbitProducer(
    "transporter_action_q", "worker.mm"
)


@RabbitListener(
    binding_key="request.download",
    queue="request_download_q",
    exchange="worker.mm",
)
def download_request_handler(msg):
    log.info("%r" % msg)
    url = json.loads(msg)["url"]
    username = json.loads(msg)["username"]
    if not Transmission.is_transmission_exist(url=url):
        with scoped_session(auto_commit=True) as s:
            user = User.get_user(s, username)
            Transmission(url=url, user_id=user.id).save(s)
    else:
        with scoped_session(auto_commit=False) as s:
            tx = Transmission.get_transmission(ssn=s, url=url)
            if tx.is_downloading or tx.is_download_fail:
                crawler_action_publisher.publish_json(
                    routing_key="crawler.download",
                    message={"download": "fail"},
                )
            elif tx.is_downloaded:
                log.warning("Download Finished!")
            else:
                log.warning("Need to upload?")


@RabbitListener(
    binding_key="request.upload",
    queue="request_upload_q",
    exchange="worker.mm",
)
def upload_request_handler(msg):
    log.info("%r" % msg)
    url = json.loads(msg)["url"]
    if not Transmission.is_transmission_exist(url=url):
        log.warning("Please download stream before upload!")
        return
    with scoped_session(auto_commit=False) as s:
        tx = Transmission.get_transmission(ssn=s, url=url)
        if tx.is_finished:
            log.warning("Uploaded Finished!")
        elif tx.is_downloaded:
            transporter_action_publisher.publish_json(
                routing_key="transporter.search", message={"url": url}
            )
        elif tx.is_uploading or tx.is_upload_fail:
            transporter_action_publisher.publish_json(
                routing_key="transporter.upload", message={"url": url}
            )
        else:
            log.warning(
                "Invalid transmission status, please download stream first!"
            )


@RabbitListener(
    binding_key="crawling.validate.status",
    queue="crawling_validate_status_q",
    exchange="worker.mm",
)
def validate_result_handler(msg):
    log.info("%r" % msg)
    result = json.loads(msg)
    url = result["url"]
    valid = result["valid"]
    if valid:
        crawler_action_publisher.publish_json(
            routing_key="crawler.download", message={"url": url}
        )
    else:
        log.warning("%s validate failed!" % url)


@RabbitListener(
    binding_key="crawling.download.status",
    queue="crawling_download_status_q",
    exchange="worker.mm",
)
def download_result_handler(msg):
    log.info("%r" % msg)
    result = json.loads(msg)
    url = result["url"]
    download = result["download"]
    if download == "downloaded":
        transporter_action_publisher.publish_json(
            routing_key="transporter.search", message={"url": url}
        )
    else:
        log.warning("Download failed, sorry")


@RabbitListener(
    binding_key="transporting.search.status",
    queue="transporting_search_status_q",
    exchange="worker.mm",
)
def search_result_handler(msg):
    log.info("%r" % msg)
    result = json.loads(msg)
    url = result["url"]
    search = result["search"]
    if search == "exist":
        log.warning("Stream already exist!")
    else:
        transporter_action_publisher.publish_json(
            routing_key="transporter.upload", message={"url": url}
        )


@RabbitListener(
    binding_key="transporting.upload.status",
    queue="transporting_upload_status_q",
    exchange="worker.mm",
)
def upload_result_handler(msg):
    log.info("%r" % msg)
    result = json.loads(msg)
    url = result["url"]
    upload = result["upload"]
    if upload == "uploaded":
        log.warning("Upload Finished! => %s" % url)
    else:
        log.warning("Upload Fail! => %s" % url)


class Manager(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self.set_interval(10)

    def poll(self):
        log.debug("Manager polling alive!")
