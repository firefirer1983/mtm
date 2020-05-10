import json
import logging
from .base.poll import Poll

from .mq.binding import Consumer, Producer
from .model.models import Transmission, User
from .model.database import scoped_session
from .mq.channel import ch

log = logging.getLogger(__file__)

crawler_action_publisher = Producer("crawler_action_q", "worker.mm")
transporter_action_publisher = Producer("transporter_action_q", "worker.mm")


@Consumer(
    binding_key="request.download",
    queue="request_download_q",
    exchange="worker.mm",
)
def download_request_handler(*args, body):
    log.info("%r" % body)
    url = json.loads(body)["url"]
    username = json.loads(body)["username"]
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


@Consumer(
    binding_key="request.upload",
    queue="request_upload_q",
    exchange="worker.mm",
)
def upload_request_handler(*args, body):
    log.info("%r" % body)
    url = json.loads(body)["url"]
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


@Consumer(
    binding_key="crawling.validate.status",
    queue="crawling_validate_status_q",
    exchange="worker.mm",
)
def validate_result_handler(*args, body):
    log.info("%r" % body)
    result = json.loads(body)
    url = result["url"]
    valid = result["valid"]
    if valid:
        crawler_action_publisher.publish_json(
            routing_key="crawler.download", message={"url": url}
        )
    else:
        log.warning("%s validate failed!" % url)


@Consumer(
    binding_key="crawling.download.status",
    queue="crawling_download_status_q",
    exchange="worker.mm",
)
def download_result_handler(*args, body):
    log.info("%r" % body)
    result = json.loads(body)
    url = result["url"]
    download = result["download"]
    if download == "downloaded":
        transporter_action_publisher.publish_json(
            routing_key="transporter.search", message={"url": url}
        )
    else:
        log.warning("Download failed, sorry")


@Consumer(
    binding_key="transporting.search.status",
    queue="transporting_search_status_q",
    exchange="worker.mm",
)
def search_result_handler(*args, body):
    log.info("%r" % body)
    result = json.loads(body)
    url = result["url"]
    search = result["search"]
    if search == "exist":
        log.warning("Stream already exist!")
    else:
        transporter_action_publisher.publish_json(
            routing_key="transporter.upload", message={"url": url}
        )


@Consumer(
    binding_key="transporting.upload.status",
    queue="transporting_upload_status_q",
    exchange="worker.mm",
)
def upload_result_handler(*args, body):
    log.info("%r" % body)
    result = json.loads(body)
    url = result["url"]
    upload = result["upload"]
    if upload == "uploaded":
        log.warning("Upload Finished! => %s" % url)
    else:
        log.warning("Upload Fail! => %s" % url)


class Manager(Poll):
    def __init__(self):
        super().__init__(ch, None)
        self.set_poll_interval(10)

    def poll(self):
        log.debug("Manager polling alive!")
