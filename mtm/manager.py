import json
import logging

from .config import MAX_DURATION
from .mq import RabbitListener, RabbitProducer, RabbitPoll
from .components.extraction import get_extraction, get_url_formatter
from .components.cache_manager import get_cache_manager
from .components.meta_crawler import MetaCrawler
from .components.cache import Material


log = logging.getLogger(__file__)

request_crawler = RabbitProducer(
    "crawler.*.request", "crawler_action_request_q", "worker.mm"
)
request_splitter = RabbitProducer(
    "splitter.*.request", "splitter_action_request_q", "worker.mm"
)

user_result_publisher = RabbitProducer(
    "user.*.result", "user_action_result_q", "worker.mm"
)

download_fail = list()


@RabbitListener(
    binding_key="user.*.request",
    queue="user_action_request_q",
    exchange="worker.mm",
)
def user_request_handler(routing_key, msg):
    log.info("%r" % msg)
    body = json.loads(msg)
    url, action = body["url"], body["action.type"]
    try:
        extraction = get_extraction(url)
    except Exception as e:
        log.exception(e)
        return
    meta_crawler = MetaCrawler()

    if extraction.is_playlist:
        playlist = meta_crawler.retrieve_playlist(extraction.url_)
        formatter = get_url_formatter(extraction.extractor)
        playlist = [formatter.get_playable_url(item) for item in playlist]
    else:
        playlist = [extraction.url_]

    mgr = get_cache_manager(extraction.extractor)

    for url in playlist:
        extraction = get_extraction(url)
        cache = mgr.find_cache(extraction.unique_id)
        if action == "download":
            if cache and cache.is_complete:
                duration_sum = sum(p.duration for p in cache.list_partials())
                if duration_sum >= cache.duration():
                    request_splitter.publish_json(
                        routing_key="splitter.split.request",
                        message={"file": cache.file_path},
                    )
                    return
            else:
                meta = meta_crawler.get_meta(url)
                if meta:
                    request_crawler.publish_json(
                        routing_key="crawler.download.request",
                        message={
                            "url": url,
                            "action.type": "download",
                            "cache_path": mgr.repo_path,
                        },
                    )
                else:
                    log.error("%s download fail!" % url)
                return

        else:
            raise NotImplementedError()


@RabbitListener(
    binding_key="*.*.result",
    queue="worker_action_result_q",
    exchange="worker.mm",
)
def worker_action_result_handler(routing_key, msg):
    print("worker action result handler")
    print(routing_key, msg)
    if routing_key == "crawler.download.result":
        body = json.loads(msg)
        result = body["result"]
        if result:
            cache_dir = body["cache_dir"]
            material = Material(cache_dir)
            if material.duration > MAX_DURATION:
                request_splitter.publish_json(
                    routing_key="splitter.split.request",
                    message={
                        "cache_dir": cache_dir,
                        "partial_duration": MAX_DURATION,
                    },
                )

    elif routing_key == "splitter.split.result":
        body = json.loads(msg)
        log.info("split done with result:", body)
    else:
        raise NotImplemented()


class Manager(RabbitPoll):
    def __init__(self, url):
        super().__init__(url)
        self.set_interval(10)

    def poll(self):
        log.debug("Manager polling alive!")
