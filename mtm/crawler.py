import json
import logging
from .components.downloader import Downloader
from .mq import (
    RabbitListener,
    RabbitProducer,
    RabbitPoll,
    RabbitRpcListener,
    RabbitRpcClient,
)


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


@RabbitListener(
    binding_key="crawler.download.request",
    queue="crawler_action_request_q",
    exchange="worker.mm",
)
def crawler_action_handler(routing_key, msg):
    log.info("%r" % msg)
    body = json.loads(msg)
    url, cache_path = body["url"], body["cache_path"]
    dwl = Downloader()
    try:
        res = dwl.download(url, cache_path)
    except Exception as e:
        msg = {"result": False, "message": "Download Fail With %s" % str(e)}
    else:
        msg = {
            "result": True,
            "message": "Download Complete",
            "cache_dir": res,
        }

    result_publisher.publish_json(
        routing_key="crawler.download.result", message=msg
    )


@RabbitRpcListener(queue="rpc_get_id")
def crawler_rpc_get_id_handler(msg):
    print(msg)
    return "crawler rpc server"


class Crawler(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self._rpc_client = RabbitRpcClient("rpc_set_id").connect(url)
        self.set_interval(10)

    def poll(self):
        log.info("polling")
