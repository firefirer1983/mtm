import json
import logging
from .base.poll import Poll

from .mq.binding import Consumer, Producer
from .model.models import Transmission, User
from .model.database import scoped_session
from .mq.channel import ch

log = logging.getLogger(__file__)

request_download_consumer = Consumer("request_q", "worker.mm")
request_upload_consumer = Consumer("request_q", "worker.mm")

status_validate_consumer = Consumer("crawling_activity_status_q", "worker.mm")
status_download_consumer = Consumer("crawling_activity_status_q", "worker.mm")
status_search_consumer = Consumer("transport_activity_status_q", "worker.mm")
status_upload_consumer = Consumer("transport_activity_status_q", "worker.mm")

crawler_action_producer = Producer("crawler_action_q", "worker.mm")
transporter_action_producer = Producer("transporter_action_q", "worker.mm")


@request_download_consumer.listen_on(binding_key="request.download")
def download_request_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    channel.basic_ack(basic_deliver.delivery_tag)
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
                channel.publish_message(
                    exchange="worker.mm", routing_key="crawler.download"
                )
            elif tx.is_downloaded:
                log.warning("Download Finished!")
            else:
                log.warning("Need to upload?")


@request_upload_consumer.listen_on(binding_key="request.upload")
def upload_request_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    channel.basic_ack(basic_deliver.delivery_tag)
    url = json.loads(body)["url"]
    if not Transmission.is_transmission_exist(url=url):
        log.warning("Please download stream before upload!")
        return
    with scoped_session(auto_commit=False) as s:
        tx = Transmission.get_transmission(ssn=s, url=url)
        if tx.is_finished:
            log.warning("Uploaded Finished!")
        elif tx.is_downloaded:
            channel.publish_message(
                exchange="worker.mm",
                routing_key="transporter.search",
                message={"url": url},
            )
        elif tx.is_uploading or tx.is_upload_fail:
            channel.publish_message(
                exchange="worker.mm",
                routing_key="transporter.upload",
                message={"url": url},
            )
        else:
            log.warning(
                "Invalid transmission status, please download stream first!"
            )


@status_validate_consumer.listen_on(binding_key="crawling.validate.status")
def validate_result_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    channel.basic_ack(basic_deliver.delivery_tag)
    result = json.loads(body)
    url = result["url"]
    valid = result["valid"]
    if valid:
        channel.publish_message(
            exchange="worker.mm",
            routing_key="crawler.download",
            message={"url": url},
        )
    else:
        log.warning("%s validate failed!" % url)


@status_download_consumer.listen_on(binding_key="crawling.download.status")
def download_result_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    channel.basic_ack(basic_deliver.delivery_tag)
    result = json.loads(body)
    url = result["url"]
    download = result["download"]
    if download == "downloaded":
        channel.publish_message(
            exchange="worker.mm",
            routing_key="transporter.search",
            message={"url": url},
        )
    else:
        log.warning("Download failed, sorry")


@status_search_consumer.listen_on(binding_key="transporting.search.status")
def search_result_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    channel.basic_ack(basic_deliver.delivery_tag)
    result = json.loads(body)
    url = result["url"]
    search = result["search"]
    if search == "exist":
        log.warning("Stream already exist!")
    else:
        channel.publish_message(
            exchange="worker.mm",
            routing_key="transporter.upload",
            message={"url": url},
        )


@status_upload_consumer.listen_on(binding_key="transporting.upload.status")
def upload_result_handler(channel, basic_deliver, properties, body):
    log.info("%r" % body)
    channel.basic_ack(basic_deliver.delivery_tag)
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
