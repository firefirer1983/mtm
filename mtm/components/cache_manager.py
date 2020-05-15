import json
import os
import logging
from pathlib import Path
import abc


log = logging.getLogger(__file__)

cache_dir_name = "cache"
default_cache_root = (
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    + "/"
    + cache_dir_name
)


def list_sub_dirs(extractor):
    for path in Path(default_cache_root).iterdir():
        if str(path) == extractor:
            return list(path.iterdir())


def parse_unique_id_from_dirname(dirname):
    head = -1
    for c in reversed(dirname):
        if c == "-":
            break
        head -= 1
    else:
        return None

    tail = dirname.find(".part.")
    if tail == -1:
        return dirname[head + 1 :]
    else:
        return dirname[head + 1 : tail]


def is_partial_of(dirname, unique_id):
    return (
        parse_unique_id_from_dirname(dirname) == unique_id
        and dirname.find(".part.") != 1
    )


class CacheManager(abc.ABC):
    def __init__(self, name):
        self._extractor = name

    @property
    def dirname(self):
        return str(self._extractor)

    @abc.abstractmethod
    def locate_cache(self, unique_id):
        pass


class Cache:
    def __init__(self, cache_info):
        self._extractor = cache_info["extractor"]
        self._cache_info = cache_info
        part_num = 0
        for d in list_sub_dirs(self._extractor):
            if is_partial_of(str(d), self.unique_id):
                part_num += 1

        self._need_split = cache_info["filesize"] / 900 >= part_num

    @property
    def need_split(self):
        return self._need_split

    def __getitem__(self, item):
        return self._cache_info.__getitem__(item)

    @property
    def unique_id(self):
        return self._cache_info["id"]


class YoutubeCache(CacheManager):
    def __init__(self):
        super().__init__("youtube")

    def locate_cache(self, unique_id):

        for d in list_sub_dirs(self.dirname):
            if (
                parse_unique_id_from_dirname(str(d)) == unique_id
                and str(d).find(".part.") == -1
            ):
                dir_ = d
                break
        else:
            return None

        json_info = None
        try:
            with open("%s/%s.info.json" % (str(dir_), unique_id), "r") as f:
                info = f.read()
                json_info = json.loads(info)
        except FileNotFoundError as e:
            log.exception(e)
        except Exception as e:
            log.exception(e)

        mm_file = str(dir_) + "/" + unique_id + ".mp3"

        if json_info["filesize"] == Path(mm_file).stat().st_size:
            return Cache(json_info)
        else:
            return None


manager_registry = [YoutubeCache()]


def get_cache_manager(extractor):
    for m in manager_registry:
        if m.dirname == extractor:
            return m
