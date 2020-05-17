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
    cache_dir, partial_duration = body["cache_dir"], body["partial_duration"]
    material = Material(cache_dir)
    split_pattern = (
        cache_dir
        + ".part.{:04d}"
        + "/"
        + material.unique_id
        + "."
        + material.ext
    )
    print("to_split:", material.data_file)
    res = split_audio(material.data_file, partial_duration, split_pattern)
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
