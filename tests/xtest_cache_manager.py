from mtm.components.cache_manager import YoutubeCache

if __name__ == '__main__':
    mgr = YoutubeCache()
    for cache in mgr.list_cache():
        if not cache.is_complete:
            print("%s left over: %u" % (cache.data_file, cache.left_over))
