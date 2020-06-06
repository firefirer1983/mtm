import os

from mtm.components.cache_manager import YoutubeCache
from mtm.config import MAX_DURATION

CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
YOUTUBE_CACHE_REPO = os.path.join(CACHE_REPO, "youtube")
if __name__ == "__main__":
    mgr = YoutubeCache()
    purge_dirs = []
    download_urls = []
    for cache in mgr.list_cache():
        if not cache.is_complete and cache.left_over > MAX_DURATION:
            download_urls.append(
                "https://www.youtube.com/watch?v=%s" % cache.unique_id)
            purge_dirs.append(cache.file_path)
        else:
            print("%s completed! total:%u left_over:%u" % (
                cache.data_file, cache.duration, cache.left_over))
    for url in download_urls:
        print("\"%s\"," % url)
    
    for d in purge_dirs:
        print("\"%s\"," % d)
