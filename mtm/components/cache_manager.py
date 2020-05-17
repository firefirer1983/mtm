import os
import logging
from pathlib import Path

from mtm.components.cache import Partial, Partials, Material
from ..utils.string_fmt import is_partial_dir, parse_unique_id
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
    return []


class CacheManager(abc.ABC):
    def __init__(self, name):
        self._extractor = name

    @property
    def dirname(self):
        return str(self._extractor)

    @abc.abstractmethod
    def find_cache(self, unique_id):
        pass

    @property
    def repo_path(self):
        return default_cache_root + "/" + self.dirname


class YoutubeCache(CacheManager):
    def __init__(self):
        super().__init__("youtube")

    def find_cache(self, unique_id):
        partials_ = Partials()
        material_ = None
        for d in list_sub_dirs(self.dirname):
            if parse_unique_id(d) == unique_id:
                if is_partial_dir(d):
                    partials_.append(Partial(d))
                else:
                    material_ = Material(d)
        if material_ and partials_:
            material_.add_partials(partials_)
        return material_


manager_registry = [YoutubeCache()]


def get_cache_manager(extractor):
    for m in manager_registry:
        if m.dirname == extractor:
            return m
