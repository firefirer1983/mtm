import json
import logging
from .components.splitter import split_audio
from mtm.components.cache import Material
from .mq import RabbitListener, RabbitProducer, RabbitPoll


log = logging.getLogger(__file__)


result_publisher = RabbitProducer(
    binding_key="*.*.result",
    queue="worker_action_result_q",
    exchange="worker.mm",
)


@RabbitListener(
    binding_key="splitter.*.request",
    queue="splitter_action_request_q",
    exchange="worker.mm",
)
def splitter_action_handler(routing_key, msg):
    log.info("%r" % msg)
    body = json.loads(msg)
    cache_dir, split_size = body["cache_dir"], body["split_size"]
    material = Material(cache_dir)
    to_split = material.data_file
    split_pattern = (
        cache_dir
        + ".part.{:04d}"
        + "/"
        + material.unique_id
        + "."
        + material.ext
    )
    print("to_split:", to_split)
    res = split_audio(to_split, material.duration, split_pattern)
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
