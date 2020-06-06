import os

from mtm.components.cache_manager import YoutubeCache
from mtm.components.splitter import split_audio
from mtm.config import MAX_DURATION

CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
YOUTUBE_CACHE_REPO = os.path.join(CACHE_REPO, "youtube")

if __name__ == "__main__":
    mgr = YoutubeCache()
    for cache in mgr.list_cache():
        if not cache.is_complete:
            continue
        if cache.is_split:
            continue
        mgr.purge_cache_partials(cache.unique_id)
        split_pattern = (
            cache.file_path + ".part.{:04d}" + "/" + cache.unique_id + "." + "m4a"
        )
        split_audio(cache.data_file, MAX_DURATION, split_pattern)
        cache.refresh_cache()
