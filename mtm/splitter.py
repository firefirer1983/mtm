import json
import logging
from .components.splitter import split_audio

from .mq import (
    RabbitListener,
    RabbitProducer,
    RabbitPoll,
)


log = logging.getLogger(__file__)


result_publisher = RabbitProducer(
    queue="worker_action_result_q", exchange="worker.mm"
)


@RabbitListener(
    binding_key="splitter.split",
    queue="worker_action_request_q",
    exchange="worker.mm",
)
def splitter_action_handler(msg):
    log.info("%r" % msg)
    cache_dir = json.loads(msg)["cache_path"]
    vid = json.loads(msg)["id"]
    fulltitle = json.loads(msg)["fulltitle"]
    duration = json.loads(msg)["duration"]
    ext = json.loads(msg)["ext"]
    to_split = "/".join([cache_dir, fulltitle, "/"]) + vid + "." + ext
    split_pattern = (
        "/".join([cache_dir, fulltitle, "/"]) + vid + ".{:04d}" + "." + ext
    )
    print("to_split:", to_split)
    res = split_audio(to_split, duration, split_pattern)
    result_publisher.publish_json(
        routing_key="splitter.split.result",
        message={
            "split": bool(res),
            "message": "split success" if bool(res) else "split fail",
            "url": res,
        },
    )


class Splitter(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self.set_interval(10)

    def poll(self):
        log.debug("splitter polling alive!")
