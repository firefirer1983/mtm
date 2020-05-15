import json
import logging
from .mq import RabbitListener, RabbitProducer, RabbitPoll
from .utils.string_fmt import parse_basic_info
from .components.cache_manager import get_cache_manager

log = logging.getLogger(__file__)

request_crawler = RabbitProducer(
    "crawler.*.request", "crawler_action_request_q", "worker.mm"
)
request_splitter = RabbitProducer(
    "splitter.*.request", "splitter_action_request_q", "worker.mm"
)


@RabbitListener(
    binding_key="user.*.request",
    queue="user_action_request_q",
    exchange="worker.mm",
)
def user_request_handler(msg):
    log.info("%r" % msg)
    body = json.loads(msg)
    url = body["url"]
    username = body["username"]
    action = body["action.type"]
    try:
        extractor, unique_id = parse_basic_info(url)
    except Exception as e:
        log.exception(e)
        return

    mgr = get_cache_manager(extractor)
    if action == "download":
        cache = mgr.locate_cache(unique_id)
        if not cache:
            request_crawler.publish_json(
                routing_key="crawler.download.request",
                message={"url": url, "action.type": "download"},
            )
            return

        if cache.need_split:
            request_splitter.publish_json(
                routing_key="splitter.split.request", message={}
            )
            return
        log.info("Nothing need to be done for %s" % url)
    else:
        raise NotImplementedError()


class Manager(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self.set_interval(10)

    def poll(self):
        log.debug("Manager polling alive!")
