import os
from multiprocessing import Queue, Process
from queue import Empty

from mtm.components.cache import Cache
from mtm.components.cache_manager import YoutubeCache
from mtm.components.mood.auth import login_context
from mtm.components.mood.channels import MMChannel
from mtm.config import MAX_DURATION
from mtm.model.models import MMStorageEntry

ORIGIN = "youtube"

CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
YOUTUBE_CACHE_REPO = os.path.join(CACHE_REPO, ORIGIN)


def upload_task(task_queue):
    with login_context("username", "password") as token:
        channel = MMChannel(token)
        try:
            while True:
                cache: Cache = task_queue.get(timeout=1)
                print("start upload %s" % cache.file_path)
                try:
                    MMStorageEntry.insert_one(
                        origin=ORIGIN,
                        unique_id=cache.unique_id,
                        full_path=cache.file_path,
                        duration=cache.duration
                    )
                except Exception as e:
                    print(str(e))
                    continue
                url, key = channel.fake_upload_audio(cache.file_path)
                MMStorageEntry.finish_upload(cache.file_path, url=url, key=key)
        
        except Empty as e:
            print("No more download")


def main():
    mgr = YoutubeCache()
    uploads = Queue()
    for cache in mgr.list_cache():
        if cache.is_complete or cache.left_over < MAX_DURATION:
            # print("%s completed! total:%u left_over:%u" % (
            #     cache.data_file, cache.duration, cache.left_over))
            partials = cache.list_partials()
            if partials:
                for partial in cache.list_partials():
                    # print("upload => %s " % partial.file_path)
                    uploads.put(partial)
            else:
                origin = cache.get_origin()
                # print("upload => %s" % origin.file_path)
                uploads.put(origin)
    
    process_num = 3  # os.cpu_count()
    prs = []
    for i in range(process_num):
        pr = Process(target=upload_task, args=(uploads,))
        pr.start()
        prs.append(pr)
    
    for pr in prs:
        pr.join()


if __name__ == "__main__":
    main()
