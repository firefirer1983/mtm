import json
import logging
from .components.downloader import Downloader, DEFAULT_AUDIO_FMT
from .mq import (
    RabbitListener,
    RabbitProducer,
    RabbitPoll,
    RabbitRpcListener,
    RabbitRpcClient,
)
from .model.models import Transmission, TxStatus
from .model.database import scoped_session


log = logging.getLogger(__file__)


result_publisher = RabbitProducer(
    binding_key="*.*.result",
    queue="worker_action_result_q",
    exchange="worker.mm",
)

splitter_request_publisher = RabbitProducer(
    binding_key="splitter.*.request",
    queue="splitter_action_request_q",
    exchange="worker.mm",
)

DEFAULT_DURATION = 15 * 60  # 15 minutes maximum length


class DownloadState:
    validate = 0
    download = 1


@RabbitListener(
    binding_key="crawler.*.request",
    queue="crawler_action_request_q",
    exchange="worker.mm",
)
def crawler_action_handler(msg):
    log.info("%r" % msg)
    url = json.loads(msg)["url"]
    dwl = Downloader(url)
    info = None
    for i, res in enumerate(dwl):
        if i == DownloadState.validate:
            print("crawler validate done!")
            result_publisher.publish_json(
                routing_key="crawler.validate.result",
                message={
                    "validate": bool(res),
                    "message": "Valid URL" if bool(res) else "Invalid URL",
                    "url": url,
                },
            )
            print("publish message done!")
            info = res
        elif i == DownloadState.download:
            print("crawler download done!")
            result_publisher.publish_json(
                routing_key="crawler.download.result",
                message={
                    "download": not bool(res),
                    "message": "Download Fail:%s" % res
                    if bool(res)
                    else "Download Finished",
                    "url": url,
                },
            )
            if info["duration"] > DEFAULT_DURATION:
                splitter_request_publisher.publish_json(
                    "splitter.split.request",
                    {
                        "duration": DEFAULT_DURATION,
                        "fulltitle": info["fulltitle"],
                        "cache_path": info["cache_path"],
                        "ext": DEFAULT_AUDIO_FMT,
                        "id": info["id"],
                    },
                )


@RabbitRpcListener(queue="rpc_get_id")
def crawler_rpc_get_id_handler(msg):
    print(msg)
    return "crawler rpc server"


class Crawler(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self._rpc_client = RabbitRpcClient("rpc_set_id").connect(url)
        self.set_interval(2)

    def poll(self):
        log.info("polling")
